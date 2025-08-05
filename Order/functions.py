import pprint

from rest_framework import status
from rest_framework.response import Response
from decimal import Decimal
from .models import OrderItem
import logging

logging.basicConfig(level=logging.INFO)

def CheckCountAndTotalPrice(data):
    items = data['items']
    total_sum = Decimal(data['total_sum'])
    logging.info(f"Total sum: {total_sum}")

    if total_sum < Decimal(500):
        return Response('Minimal sum is not enough', status=status.HTTP_400_BAD_REQUEST)

    return False


def createOrderItems(data, order):
    pprint.pprint(data)
    items = [
        OrderItem(
            order=order,  # Ссылаемся на только что созданный заказ
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['total_item_price'],
            sku=item['sku']
        ) for item in data['items']
    ]

    try:
        return OrderItem.objects.bulk_create(items)
    except Exception as e:
        logging.error(f"Error creating order items: {e}")
        raise


