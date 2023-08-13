import json

from rest_framework import serializers

from .models import Activity, Recommendation


class ActivityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "category", "slug", "name", "thumbnail_path", "resources"]

    def to_representation(self, instance):
        data = super(ActivityDetailSerializer, self).to_representation(instance)
        clear_json = str(instance.resources).strip("'<>() ").replace("'", '"')
        resources = json.loads(clear_json)
        # Remove credential qna
        resources["data"].pop("secretKey", None)
        data["resources"] = resources
        return data


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "category", "slug", "name", "thumbnail_path", "created_at"]


class ActivityRecommendationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source="activity_id")
    category = serializers.CharField(read_only=True, source="activity_id__category")
    slug = serializers.CharField(read_only=True, source="activity_id__slug")
    name = serializers.CharField(read_only=True, source="activity_id__name")
    thumbnail_path = serializers.CharField(
        read_only=True,
        style={"base_template": "textarea.html"},
        source="activity_id__thumbnail_path",
    )
    created_at = serializers.DateTimeField(
        read_only=True, source="activity_id__created_at"
    )

    class Meta:
        model = Recommendation
        fields = ["id", "category", "slug", "name", "thumbnail_path", "created_at"]
