import logging
import uuid
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
import requests
from rest_framework.response import Response
from Order.models import Order, OrderItem
from Order.serializers import OrderSerializer, OrderDetailSerializer
import json
from .producer import SendToProducer
from .constants import basket_url
from .functions import CheckCountAndTotalPrice, createOrderItems

# Настройка логирования
logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid data for order creation: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Проверка корзины
            basket_id = serializer.validated_data['basket_id']
            if not basket_id:
                return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Fetching basket with ID: {basket_id}")
            basket_response = requests.get(f"{basket_url}/cart/{basket_id}/items/")

            if basket_response.status_code == 404:
                logger.warning(f"Basket {basket_id} not found")
                return Response('Basket not found', status=status.HTTP_404_NOT_FOUND)
            if basket_response.status_code != 200:
                logger.error(f"Failed to fetch basket {basket_id}: {basket_response.text}")
                return Response('Basket service error', status=status.HTTP_503_SERVICE_UNAVAILABLE)

            basket_data = basket_response.json()
            not_verified = CheckCountAndTotalPrice(basket_data)
            if not_verified:
                logger.warning(f"Basket verification failed: {not_verified}")
                return not_verified

            # Проверка идемпотентности: проверяем, не создан ли уже заказ для этой корзины
            if Order.objects.filter(basket_id=basket_id).exists():
                logger.info(f"Order for basket {basket_id} already exists")
                existing_order = Order.objects.get(basket_id=basket_id)
                return Response(OrderSerializer(existing_order).data, status=status.HTTP_200_OK)

            # Транзакция для создания заказа и элементов
            with transaction.atomic():
                order_data = {
                    'customer': serializer.validated_data['customer'],
                    'total_sum': Decimal(basket_data['total_sum']),
                    'basket_id': basket_id,
                    'shipping_address': serializer.validated_data['shipping_address'],
                    'payment_method': serializer.validated_data['payment_method'],
                    'msg_for_couriers': serializer.validated_data['msg_for_couriers'],
                    'msg_for_order': serializer.validated_data['msg_for_order'],
                    'status': 'pending',  # Начальный статус
                    'store_id': int(basket_data['store_id']),
                }

                order_serializer = OrderSerializer(data=order_data)
                order_serializer.is_valid(raise_exception=True)
                order = order_serializer.save()
                logger.info(f"Order created with ID: {order.id}")

                # Создание элементов заказа
                order_items = createOrderItems(basket_data, order)
                order_items_serializer = OrderDetailSerializer(order_items, many=True)
                logger.info(f"Order items created for order {order.id}")

                data_for_courier = {
                    'customer': serializer.validated_data['customer'],
                    'shipping_address': serializer.validated_data['shipping_address'],
                    'msg_for_couriers': serializer.validated_data['msg_for_couriers'],
                    'store_id': int(basket_data['store_id']),
                    'order_id': str(order.id),
                    'additional_number': "4545",
                    'priority': 1,
                }
            try:

                basket_id = {'basket_id': str(basket_id)}
                # SendToProducer(basket_id, "BasketIsOrdered")
                logger.info(f"Sent order {basket_id} to BasketApi")
                SendToProducer(data_for_courier, "OrderComingToCourier")
                logger.info(f"Sent order {basket_id} to CouriersApi")
                SendToProducer(str(order_items_serializer.data), "SentToCollectorsApi")
                logger.warning(order_items_serializer.data)
                logger.info(f"Sent order {order.id} to collectors")
            except Exception as e:
                logger.error(f"Failed to send order {order.id} to collectors: {str(e)}")
                order.delete()
                return Response('Collectors service unavailable', status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(f"Unexpected error during order creation: {str(e)}")
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderDetailSerializer

