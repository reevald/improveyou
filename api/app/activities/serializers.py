import json

from rest_framework import serializers

from .models import Activity


class ActivityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "category", "slug", "name", "thumbnail_path", "resources"]

    def to_representation(self, instance):
        data = super(ActivityDetailSerializer, self).to_representation(instance)
        clear_json = str(instance.resources).strip("'<>() ").replace("'", '"')
        data["resources"] = json.loads(clear_json)
        return data
