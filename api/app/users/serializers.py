import django.contrib.auth.password_validation as validators
from django.conf import settings
from django.core import exceptions
from django.core.validators import EmailValidator
from django.utils import timezone
from items.serializers import ItemBagSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import GameStat, Object, User


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate(self, data):
        instance_user = self.Meta.model(**data)
        password = data["password"]
        errors = dict()
        try:
            # Based on AUTH_PASSWORD_VALIDATORS
            # See: config/django/settings/base.py
            validators.validate_password(password=password, user=instance_user)

        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(RegisterUserSerializer, self).validate(data)

    def create(self, validated_data):
        raw_password = validated_data.pop("password", None)
        instance_user = self.Meta.model(**validated_data)
        if raw_password is not None:
            # Assign password field with password-hashed based on PASSWORD_HASHERS
            # See: config/django/settings/base.py
            instance_user.set_password(raw_password)
        instance_user.save()
        return instance_user


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
            "password": {"required": True},
        }

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = self.Meta.model.objects.get(email=email)
        except self.Meta.model.DoesNotExist:
            raise AuthenticationFailed(
                "Sorry, that email doesn't exist. Please try again."
            )
        if not user.check_password(password):
            raise AuthenticationFailed(
                "Sorry, that password isn't right. Please try again."
            )
        data["user"] = user  # For credential jwt & update last login
        return data


class UserObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ["character_id", "hat_id", "clothes_id", "shoes_id"]


class UserGameStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStat
        fields = [
            "gold",
            "poin_brain",
            "poin_heart",
            "poin_muscle",
            "streak_current",
            "streak_percent_interest",
        ]


class UserChangeUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "last_username_changed"]
        extra_kwargs = {"username": {"required": True}}

    def update(self, instance, validated_data):
        if instance.username == validated_data.get("username"):
            raise serializers.ValidationError(
                {"username": ["This field must be not same with currently in use"]}
            )
        now = timezone.now()
        if now - instance.last_username_changed < settings.USERNAME_CHANGE_PERIOD:
            raise serializers.ValidationError(
                "You can't change username right now because you've changed it "
                f"once within {settings.USERNAME_CHANGE_PERIOD.days} days"
            )

        instance.username = validated_data.get("username")
        instance.last_username_changed = now
        instance.save()
        return instance


class UserChangePublicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_public_mode"]
        extra_kwargs = {"is_public_mode": {"required": True}}

    def update(self, instance, validated_data):
        if instance.is_public_mode == validated_data.get("is_public_mode"):
            raise serializers.ValidationError(
                {
                    "is_public_mode": [
                        "This field must be not same with currently in use"
                    ]
                }
            )
        instance.is_public_mode = validated_data.get("is_public_mode")
        instance.save()
        return instance


class UserBagItemSerializer(serializers.ModelSerializer):
    bag_items = ItemBagSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["bag_items"]
