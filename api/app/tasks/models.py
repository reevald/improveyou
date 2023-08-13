import uuid

from activities.models import ACTIVITY_CATEGORIES
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

POIN_TYPES = [
    ("poin_brain", "POIN BRAIN"),
    ("poin_heart", "POIN HEART"),
    ("poin_muscle", "POIN MUSCLE"),
]

TARGET_TYPES = [("time", "TIME"), ("amount", "AMOUNT")]

TARGET_UNITS = [("second", "SECOND"), ("star", "STAR"), ("did", "DID")]


class Task(models.Model):
    # One activity_category = one task (to simplify)
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    activity_category = models.CharField(choices=ACTIVITY_CATEGORIES, max_length=32)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    reward_poin_type = models.CharField(choices=POIN_TYPES, max_length=32)
    reward_poin_value = models.IntegerField(blank=True, null=True)
    target_type = models.CharField(choices=TARGET_TYPES, max_length=32)
    target_value = models.IntegerField(blank=True, null=True)
    target_unit = models.CharField(
        choices=TARGET_UNITS,
        max_length=32,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tasks"
