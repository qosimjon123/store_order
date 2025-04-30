from rest_framework import serializers

from Order.models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):

    is_locked = serializers.BooleanField(read_only=True)
    cancel_reason = serializers.CharField(read_only=True)
    class Meta:
        model = Order
        fields = ['pk', 'customer', 'basket_id' ,'total_price',
                  'shipping_address', 'payment_method',
                  'is_locked', 'msg_for_couriers', 'msg_for_order',
                  'cancel_reason']



class OrderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem

        fields = '__all__'
