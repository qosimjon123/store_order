from rest_framework import viewsets, status
import requests
from Order.models import Order, OrderItem
from Order.serializers import OrderSerializer, OrderDetailSerializer
from rest_framework.response import Response

from .constants import basket_url
from .functions import CheckCountAndTotalPrice


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




            return Response(OrderSerializer(serializer.data).data, status=status.HTTP_200_OK)


        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderDetailSerializer
