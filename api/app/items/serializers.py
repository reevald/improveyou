from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from users.models import Bag, GameStat

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


class BuyItemSerializer(serializers.ModelSerializer):
    # 1) Check item_id available in shop or not (also get price etc)
    # 2) Get user game stat (gold, poin, etc)
    # 3) Calculate total price and game stat user (buy or not enough)
    # 4) Insert item_id in bag (reject if already have, w/ unique pairs)
    # 5) Update user game stat
    item_id = serializers.UUIDField()

    class Meta:
        model = GameStat
        fields = ["item_id"]
        extra_kwargs = {"item_id": {"required": True}}
        depth = 1

    def update(self, instance, validated_data):
        try:
            # 1
            shop_item = Item.objects.get(
                id=validated_data.get("item_id"), availability="shop"
            )
            # 2
            user_gamestat = GameStat.objects.values(
                "gold", "poin_brain", "poin_heart", "poin_muscle"
            ).get(user_id=instance.id)
        except Item.DoesNotExist:
            raise ParseError("Request contains malformed data")
        except GameStat.DoesNotExist:
            raise serializers.ValidationError("User data not found")

        # 3
        # Each item in shop must have price
        total_price = shop_item.price_value
        type_price = shop_item.price_type
        discount_type = shop_item.discount_type
        discount_value = shop_item.discount_value or 0

        if (
            not total_price
            or not type_price
            or (discount_type == "amount" and discount_value > total_price)
            or (discount_type == "percent" and discount_value > 100)
        ):
            raise serializers.ValidationError("Invalid data item")

        if discount_type == "amount":
            total_price -= discount_value
        if discount_type == "percent":
            total_price -= int(discount_value * total_price / 100)

        if user_gamestat[type_price] < total_price:
            raise serializers.ValidationError("Gold or poin not enough to buy the item")

        # 4
        instance_bag = Bag(user_id=instance, item_id=shop_item, source_type="shop")

        # 5
        instance = self.Meta.model(user_id=instance)
        setattr(instance, type_price, user_gamestat[type_price] - total_price)

        # Wrap with database transactions
        try:
            with transaction.atomic():
                instance_bag.save()
                instance.save(update_fields=[type_price])
        except IntegrityError:
            raise serializers.ValidationError("Transaction failed")
        return instance
