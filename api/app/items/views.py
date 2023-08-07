from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from users.auths import JWTAuthentication

from .models import Item
from .serializers import BuyItemSerializer, ItemShopSerializer


class ShopItemView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        shop_items = Item.objects.filter(availability="shop")
        serializer = ItemShopSerializer(shop_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuyItemView(APIView):
    throttle_scope = "buy_item"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = BuyItemSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
