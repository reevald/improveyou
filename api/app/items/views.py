from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from users.auths import JWTAuthentication

from .models import Item
from .serializers import ItemShopSerializer


class ShopItemView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        shop_items = Item.objects.filter(availability="shop")
        serializer = ItemShopSerializer(shop_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
