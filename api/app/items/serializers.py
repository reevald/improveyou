from rest_framework import serializers

from .models import Item


class ItemBagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "category", "name", "rarity", "thumbnail_path"]


class ItemShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "id",
            "category",
            "name",
            "rarity",
            "thumbnail_path",
            "price_type",
            "price_value",
            "discount_type",
            "discount_value",
        ]
