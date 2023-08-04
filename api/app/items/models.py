import uuid

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

ITEM_CATEGORIES = [
    ("character", "CHARACTER"),
    ("background", "BACKGROUND"),
    ("hat", "HAT"),
    ("shirt", "SHIRT"),
    ("trouser", "TROUSER"),
]

ITEM_RARITIES = [
    ("common", "COMMON"),  # green
    ("rare", "RARE"),  # blue
    ("epic", "EPIC"),  # purple
    ("mythic", "MYTHIC"),  # orange
]

PRICE_TYPES = [
    ("gold", "GOLD"),
    ("poin_brain", "POIN BRAIN"),
    ("poin_heart", "POIN HEARTH"),
    ("poin_muscle", "POIN MUSCLE"),
]

AVAILABILITIES = [("none", "NONE"), ("shop", "SHOP"), ("event", "EVENT")]

DISCOUNT_TYPES = [("none", "NONE"), ("percent", "PERCENT"), ("amount", "AMOUNT")]


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    category = models.CharField(choices=ITEM_CATEGORIES, max_length=32)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    rarity = models.CharField(choices=ITEM_RARITIES, max_length=32)
    price_type = models.CharField(choices=PRICE_TYPES, max_length=32)
    price_value = models.IntegerField(blank=True, null=True)
    availability = models.CharField(
        choices=AVAILABILITIES, default="none", max_length=32
    )
    discount_type = models.CharField(
        choices=DISCOUNT_TYPES, default="none", max_length=32
    )
    discount_value = models.IntegerField(blank=True, null=True)
    thumbnail_path = models.TextField(blank=True, null=True)
    sprite_path = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "items"
