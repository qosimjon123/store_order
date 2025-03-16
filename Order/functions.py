import pprint

from rest_framework import status
from rest_framework.response import Response


def CheckCountAndTotalPrice(data):
    items = data['items']
    total_sum = int(data['total_sum'])
    pprint.pprint(total_sum)

    if total_sum < 500:
        return Response('Minimal sum is not enough', status=status.HTTP_400_BAD_REQUEST)
