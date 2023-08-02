import django.contrib.auth.password_validation as validators
from django.core import exceptions
from rest_framework import serializers

from .models import User


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
        fields = ["id"]
