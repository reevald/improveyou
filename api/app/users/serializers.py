import json

import django.contrib.auth.password_validation as validators
from django.conf import settings
from django.core import exceptions
from django.core.validators import EmailValidator
from django.db import IntegrityError
from django.db.models import Case, ExpressionWrapper, F, IntegerField, When
from django.utils import timezone
from items.models import Item
from items.serializers import ItemBagSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ParseError

from .models import Bag, DailyCheck, DailyCheckQuestion, GameStat, Object, TaskLog, User


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
    character_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="character_id__sprite_path"
    )
    hat_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="hat_id__sprite_path"
    )
    clothes_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="clothes_id__sprite_path"
    )
    shoes_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="shoes_id__sprite_path"
    )
    background_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="background_id__sprite_path"
    )

    class Meta:
        model = Object
        fields = [
            "character_sprite",
            "hat_sprite",
            "clothes_sprite",
            "shoes_sprite",
            "background_sprite",
        ]


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


class UserBagEquipItemSerializer(serializers.ModelSerializer):
    # 1) Check item owned or not
    # 2) If yes, equip it and change object data
    item_id = serializers.UUIDField()

    class Meta:
        model = Object
        fields = [
            "character_id",
            "hat_id",
            "clothes_id",
            "shoes_id",
            "background_id",
            "item_id",
        ]
        extra_kwargs = {"item_id": {"required": True}}
        # Don't need more query for each field (items) (depth = 1 / flat)
        depth = 1

    def update(self, instance, validated_data):
        try:
            bag_item = Bag.objects.values(
                "user_id", "item_id", "item_id__category"
            ).get(user_id=instance.id, item_id=validated_data.get("item_id"))
        except Bag.DoesNotExist:
            raise ParseError("Request contains malformed data")

        category_id = bag_item["item_id__category"] + "_id"

        # Overide instance User => instance Object
        instance = self.Meta.model(user_id=instance)

        # Change <category>_id, check ITEM_CATEGORIES in Item model
        setattr(instance, category_id, Item(id=bag_item["item_id"]))

        instance.save(update_fields=[category_id])
        return instance


class UserDailyCheckQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCheckQuestion
        fields = [
            "id",
            "question",
            "type_answer",
            "limited_answer",
        ]

    def to_representation(self, instance):
        data = super(UserDailyCheckQuestionSerializer, self).to_representation(instance)
        clear_json = str(instance.limited_answer).strip("'<>() ").replace("'", '"')
        data["limited_answer"] = json.loads(clear_json)
        return data


class UserDailyCheckSerializer(serializers.ModelSerializer):
    qna = serializers.ListField(
        min_length=0, max_length=settings.MAX_DAILY_CHECK_OTHER_QUESTIONS
    )
    streak_status = serializers.ChoiceField(choices=["none", "continue", "discontinue"])

    class Meta:
        model = DailyCheck
        fields = [
            "qna",
            "streak_status",
        ]
        extra_kwargs = {
            "qna": {"required": True},
            "streak_status": {"required": True},
        }

    def create(self, validated_data):
        # Schema of qna
        # {
        #     "streak_status": "something"
        #     "qna": [
        #         {
        #             "question_id": "something",
        #             "user_answer": "something"
        #         }
        #     ]
        # }
        instance_user = self.context["user"]
        other_questions = []
        for qna in validated_data.get("qna"):
            question_id = qna.get("question_id")
            user_answer = qna.get("user_answer")
            if not question_id or not user_answer:
                raise ParseError("Request contains malformed data")
            other_questions.append(question_id)

        # Validation list of question_id
        if len(other_questions) > 0:
            qna = DailyCheckQuestion.objects.filter(
                pk__in=[i["question_id"] for i in other_questions]
            )
            if len(qna) == 0:
                raise serializers.ValidationError("Invalid other questions")

        instance = self.Meta.model(
            user_id=instance_user,
            date_target=timezone.now().date(),
            streak_status=validated_data.get("streak_status"),
            other_questions=json.dumps(other_questions),
        )

        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                "Dailycheck already filled in today or something wrong"
            )

        # Impact:
        # Update gamestat (current streak & percent interest streak)
        # https://docs.djangoproject.com/en/4.2/ref/models/conditional-expressions/
        # https://docs.djangoproject.com/en/4.2/ref/models/expressions/#using-f-with-annotations
        # 1) When continue streak +1 else 0
        # 2) Max streak percent interest 50% else 0-9=>0%, 10-19=>10%, etc
        GameStat.objects.filter(user_id=instance_user).update(
            streak_current=F("streak_current") + 1
            if validated_data.get("streak_status") == "continue"
            else 0,
            streak_percent_interest=Case(
                When(streak_current__gte=49, then=50),
                When(
                    streak_current__lt=49,
                    then=ExpressionWrapper(
                        # In this stage, streak current already updated +1
                        F("streak_current") - F("streak_current") % 10,
                        output_field=IntegerField(),
                    ),
                ),
            )
            if validated_data.get("streak_status") == "continue"
            else 0,
        )

        return instance


class UserTaskProgressSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source="task_id__id")
    activity_category = serializers.CharField(
        read_only=True, source="task_id__activity_category"
    )
    name = serializers.CharField(read_only=True, source="task_id__name")
    reward_poin_type = serializers.CharField(
        read_only=True, source="task_id__reward_poin_type"
    )
    reward_poin_value = serializers.IntegerField(
        read_only=True, source="task_id__reward_poin_value"
    )
    target_type = serializers.CharField(read_only=True, source="task_id__target_type")
    target_value = serializers.IntegerField(
        read_only=True, source="task_id__target_value"
    )
    target_unit = serializers.CharField(read_only=True, source="task_id__target_unit")

    class Meta:
        model = TaskLog
        fields = [
            "id",
            "activity_category",
            "name",
            "reward_poin_type",
            "reward_poin_value",
            "target_type",
            "target_value",
            "target_unit",
            "current_progress",
            "completed_at",
        ]


class UserEventRewardSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(read_only=True, source="event__id")
    event_name = serializers.CharField(read_only=True, source="event__name")

    class Meta:
        model = Item
        fields = [
            "id",
            "event_id",
            "event_name",
            "category",
            "name",
            "rarity",
            "thumbnail_path",
            "availability",
        ]
