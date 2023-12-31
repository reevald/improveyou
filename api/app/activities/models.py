import uuid

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

ACTIVITY_CATEGORIES = [
    ("exercise", "EXERCISE"),
    ("meditation", "MEDITATION"),
    ("reading", "READING"),
]

URGE_LEVELS = [
    ("very_low", "VERY_LOW"),
    ("low", "LOW"),
    ("medium", "MEDIUM"),
    ("high", "HIGH"),
    ("very_heigh", "VERY_HEIGH"),
]


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    category = models.CharField(choices=ACTIVITY_CATEGORIES, max_length=32)
    slug = models.CharField(
        max_length=100, validators=[MinLengthValidator(2)], unique=True
    )
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    thumbnail_path = models.TextField(blank=True, null=True)
    resources = models.TextField(blank=True, null=True)
    # Schema of resources
    # Save (to string): json.dumps(dict) and loads (to dict) : json.loads(string)
    # {
    #     "type": "POSE", # POSE, AUDIO, READ
    #     "data": {
    #         "modules": [
    #             "/path/tfjs.js",
    #         ],
    #         "modelJSON": "/path/model.json",
    #         "guidePictures": [
    #             "/path/step1.jpg",
    #             "/path/step2.jpg"
    #         ],
    #         "target": {
    #             "type": "TIME", # TIME or AMOUNT
    #             "values": [60, 120, 180],
    #             "unit":  "SECOND" # SECOND or STAR
    #         }
    #     },
    # }
    # {
    #     "type": "AUDIO", # POSE, AUDIO, READ
    #     "data": {
    #         "modules": [
    #             "/path/audio.js",
    #         ],
    #         "audioPath": "/path/audio.mp3",
    #         "guidePictures": [
    #             "/path/step1.jpg",
    #             "/path/step2.jpg"
    #         ],
    #         "target": {
    #             "type": "TIME", # TIME or AMOUNT
    #             "values": [60, 120, 180],
    #             "unit":  "SECOND" # SECOND or STAR
    #         }
    #     },
    # }
    # {
    #     "type": "READ", # POSE, AUDIO, READ
    #     "data": {
    #         "modules": [
    #             "/path/read.js",
    #         ],
    #         "articlePath": "/path/artikel.html",
    #         "qnaPath": "/path/qna.json",
    #         "secretKey": "1idh9asiuhdji1niune91123dsad", # base64
    #         "secret"
    #         "guidePictures": [
    #             "/path/step1.jpg",
    #             "/path/step2.jpg"
    #         ],
    #         "target": {
    #             "type": "AMOUNT", # TIME or AMOUNT
    #             "values": [10],
    #             "unit":  "STAR" # SECOND or STAR
    #         },
    #         "attempt": 3 # hearth
    #     },
    # }
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "activities"


class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    urge_level = models.CharField(choices=URGE_LEVELS, default="medium", max_length=32)
    activity_id = models.ForeignKey(
        Activity, on_delete=models.CASCADE, db_column="activity_id"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"[💃 {self.urge_level}]" + f"[🏃 {self.activity_id}]"

    class Meta:
        db_table = "activities_recommendations"
