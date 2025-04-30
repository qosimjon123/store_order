import pprint
from decimal import Decimal

from rest_framework import viewsets, status
import requests
from Order.models import Order, OrderItem
from Order.serializers import OrderSerializer, OrderDetailSerializer
from rest_framework.response import Response

from .producer import SendToProducer
from .constants import basket_url
from .functions import CheckCountAndTotalPrice, createOrderItems



# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            basket = requests.get(
                "{}/cart/{}/items/".format(basket_url, serializer.validated_data['basket_id']),
            )

            if basket.status_code == 404:
                return Response('Basket not found', status=status.HTTP_404_NOT_FOUND)

            not_verified = CheckCountAndTotalPrice(basket.json())

            if not_verified:
                return not_verified


            order_data = {
                'customer': serializer.validated_data['customer'],
                'total_sum': Decimal(basket.json()['total_sum']),
                'basket_id': serializer.validated_data['basket_id'],
                'shipping_address': serializer.validated_data['shipping_address'],
                'payment_method': serializer.validated_data['payment_method'],
                'msg_for_couriers': serializer.validated_data['msg_for_couriers'],
                'msg_for_order': serializer.validated_data['msg_for_order'],
            }


            order_serializer = OrderSerializer(data=order_data)
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

            order_items = createOrderItems(basket.json(), order)

            order_items_serializator = OrderDetailSerializer(order_items, many=True)

            basket_id = { 'basket_id': str(order.basket_id)}
            order_items = {'order_items': str(order_items_serializator.data)}
            SendToProducer(basket_id, "BasketIsOrdered")
            pprint.pprint(order_items)
            SendToProducer(order_items, "SentToCollectorsApi")


            return Response(OrderSerializer(serializer.data).data, status=status.HTTP_200_OK)


        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderDetailSerializer
