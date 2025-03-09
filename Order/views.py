from django.shortcuts import render
from rest_framework import viewsets

from Order.models import Order, OrderItem
from Order.serializers import OrderSerializer, OrderDetailSerializer


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderDetailSerializer
