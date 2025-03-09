from rest_framework import serializers

from Order.models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'



class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
