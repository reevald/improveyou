import base64
import json

import django.contrib.auth.password_validation as validators
from activities.models import Activity
from django.conf import settings
from django.core import exceptions
from django.core.validators import EmailValidator
from django.db import IntegrityError
from django.db.models import Case, ExpressionWrapper, F, IntegerField, When
from django.utils import timezone
from items.models import ITEM_CATEGORIES, Item
from items.serializers import ItemBagSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ParseError
from schema import And, Schema, SchemaError
from tasks.models import Task

from .models import (
    ActivityLog,
    Bag,
    DailyCheck,
    DailyCheckQuestion,
    GameStat,
    Object,
    TaskLog,
    User,
)


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
    obj_character_id = serializers.UUIDField(source="character_id")
    obj_hat_id = serializers.UUIDField(source="hat_id")
    obj_clothes_id = serializers.UUIDField(source="clothes_id")
    obj_shoes_id = serializers.UUIDField(source="shoes_id")
    obj_background_id = serializers.UUIDField(source="background_id")
    obj_character_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="character_id__sprite_path"
    )
    obj_hat_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="hat_id__sprite_path"
    )
    obj_clothes_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="clothes_id__sprite_path"
    )
    obj_shoes_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="shoes_id__sprite_path"
    )
    obj_background_sprite = serializers.CharField(
        style={"base_template": "textarea.html"}, source="background_id__sprite_path"
    )

    class Meta:
        model = Object
        fields = [
            "obj_character_id",
            "obj_character_sprite",
            "obj_hat_id",
            "obj_hat_sprite",
            "obj_clothes_id",
            "obj_clothes_sprite",
            "obj_shoes_id",
            "obj_shoes_sprite",
            "obj_background_id",
            "obj_background_sprite",
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
    item_id = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = Object
        fields = ["item_id"]
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


class UserBagUnequipItemSerializer(serializers.ModelSerializer):
    category = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Object
        fields = ["category"]
        depth = 1

    def validate(self, data):
        if data["category"] not in [cat[0] for cat in ITEM_CATEGORIES]:
            raise serializers.ValidationError("Invalid category")
        return data

    def update(self, instance, validated_data):
        category_id = validated_data.get("category") + "_id"
        # Overide instance User => instance Object
        instance = self.Meta.model(user_id=instance)

        # Change <category>_id, check ITEM_CATEGORIES in Item model
        setattr(instance, category_id, None)

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
        try:
            data["limited_answer"] = json.loads(clear_json)
        except ValueError:
            raise serializers.ValidationError("Failed load data question-answer")

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

        yesterday_date = timezone.now().date() - timezone.timedelta(days=1)

        instance = self.Meta.model(
            user_id=instance_user,
            date_target=yesterday_date,
            streak_status=validated_data.get("streak_status"),
            other_questions=json.dumps(other_questions),
        )

        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                "Dailycheck already filled in today or something wrong"
            )

        grow_streak = False
        # Check if two days ago still continue or not
        if self.Meta.model.objects.filter(
            user_id=instance_user.id,
            date_target=yesterday_date - timezone.timedelta(days=1),
            streak_status="continue",
        ).exists():
            # Condition yesterday
            if validated_data.get("streak_status") == "continue":
                grow_streak = True
        else:
            # Condition first join = today
            if instance_user.date_joined.date() > yesterday_date:
                grow_streak = True

        # Impact:
        # Update gamestat (current streak & percent interest streak)
        # https://docs.djangoproject.com/en/4.2/ref/models/conditional-expressions/
        # https://docs.djangoproject.com/en/4.2/ref/models/expressions/#using-f-with-annotations
        # 1) When continue streak +1 else 0
        # 2) Max streak percent interest 50% else 0-9=>0%, 10-19=>10%, etc
        GameStat.objects.filter(user_id=instance_user).update(
            streak_current=F("streak_current") + 1
            if validated_data.get("streak_status") == "continue" and grow_streak
            else 1
            if validated_data.get("streak_status") == "continue" and not grow_streak
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


class UserActivityStartSerializer(serializers.ModelSerializer):
    # Schema of request body [POST]
    # {
    #     "activity_id": "123y3hu13-ij12hi312hu",
    #     "activity_data": {
    #         "target": {
    #             "type": "AMOUNT",
    #             "value_choosed": 20,
    #             "unit": "STAR"
    #         },
    #     }
    # }
    activity_id = serializers.UUIDField(write_only=True, required=True)
    activity_data = serializers.DictField(write_only=True, required=True)

    class Meta:
        model = ActivityLog
        fields = ["activity_id", "activity_data"]

    def validate(self, data):
        try:
            activity_data_schema = Schema(
                {
                    "target": {
                        "type": And(str, lambda s: s in ("TIME", "AMOUNT")),
                        "value_choosed": And(int, lambda i: i > 0),
                        "unit": And(str, lambda s: s in ("SECOND", "STAR")),
                    }
                }
            )
            data["activity_data"] = Schema(activity_data_schema).validate(
                data["activity_data"]
            )
        except SchemaError:
            raise serializers.ValidationError("Invalid activity_data schema")
        return data

    def create(self, validated_data):
        # 1) Get detail activity
        try:
            request_target = validated_data.get("activity_data")["target"]
            activity = Activity.objects.values("category", "resources").get(
                id=validated_data.get("activity_id")
            )
            str_resources = str(activity["resources"]).strip("'<>() ").replace("'", '"')
            dict_resources = json.loads(str_resources)
        except Activity.DoesNotExist:
            raise ParseError("Request contains malformed data")
        except ValueError:
            raise serializers.ValidationError("Failed load resources")

        # 2) Check activity_data
        # Validate target if reading activity
        if activity["category"] == "reading" and (
            request_target["type"] != "AMOUNT"
            or request_target["unit"] != "STAR"
            or request_target["value_choosed"]
            not in dict_resources["data"]["target"]["values"]
        ):
            raise serializers.ValidationError("Invalid reading activity_data")

        # Validate target if exercise/meditation activity
        if (
            activity["category"] == "exercise" or activity["category"] == "meditation"
        ) and (
            request_target["type"] != "TIME"
            or request_target["unit"] != "SECOND"
            or request_target["value_choosed"]
            not in dict_resources["data"]["target"]["values"]
        ):
            raise serializers.ValidationError(
                "Invalid exercise or meditation activity_data"
            )

        # Prepare track data
        track_data = {
            "target": {
                "type": request_target["type"],
                "current": 0,
                "goals": request_target["value_choosed"],
                "unit": request_target["unit"],
            }
        }

        if activity["category"] == "reading":
            track_data["attempt"] = {
                "current": 0,
                "max": dict_resources["data"]["attempt"],
            }
            track_data["secret_key"] = dict_resources["data"]["secretKey"]
            # Data track logs will be handled by other api (activity/quiz)
            track_data["logs"] = {}

        # 3) Try update if exist
        num_updated = self.Meta.model.objects.filter(
            user_id=self.context["user"].id,
            activity_id=validated_data.get("activity_id"),
            finished=False,
        ).update(track=json.dumps({"type": dict_resources["type"], "data": track_data}))

        instance = self.Meta.model(
            user_id=self.context["user"],
            activity_id=Activity(id=validated_data.get("activity_id")),
            play_at=timezone.now(),
            track=json.dumps({"type": dict_resources["type"], "data": track_data}),
        )

        # 4) If not exist create instead
        if num_updated == 0:
            try:
                instance.save()
            except IntegrityError:
                raise serializers.ValidationError("Activity log already filled")

        return instance


class UserActivityFinishSerializer(serializers.ModelSerializer):
    # This serializer only for exercise and meditation activity [POSE/AUDIO]
    activity_id = serializers.UUIDField(write_only=True, required=True)
    activity_finished = serializers.BooleanField(read_only=True)
    activity_remain_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["activity_id", "activity_finished", "activity_remain_time"]

    @staticmethod
    def do_impacts(user_instance, list_tasklog, activity_category, activity_result):
        data_impacts = {
            "tasklog": False,
            "data_tasklog": {},
            "gamestat": False,
            "data_gamestat": {},
        }
        try:
            for tasklog in list_tasklog:
                if tasklog["task_id__activity_category"] == activity_category:
                    if not tasklog["completed_at"]:
                        data_impacts["tasklog"] = True
                        data_impacts["data_tasklog"]["id"] = tasklog["id"]

                        # Three possible units: second or did or star
                        current_progress = tasklog["current_progress"]
                        if tasklog["task_id__target_unit"] == "did":
                            current_progress += 1
                        else:
                            current_progress += activity_result

                        data_impacts["data_tasklog"][
                            "current_progress"
                        ] = current_progress

                        if (
                            data_impacts["data_tasklog"]["current_progress"]
                            >= tasklog["task_id__target_value"]
                        ):
                            data_impacts["data_tasklog"]["completed"] = True
                            data_impacts["gamestat"] = True
                            data_impacts["data_gamestat"]["reward_poin_type"] = tasklog[
                                "task_id__reward_poin_type"
                            ]
                            data_impacts["data_gamestat"][
                                "reward_poin_value"
                            ] = tasklog["task_id__reward_poin_value"]
                        else:
                            data_impacts["data_tasklog"]["completed"] = False

                    # To simplify one category = one task
                    raise StopIteration
        except StopIteration:
            pass

        if data_impacts["tasklog"]:
            TaskLog.objects.filter(
                id=data_impacts["data_tasklog"]["id"],
                user_id=user_instance.id,
                created_at=timezone.now().date(),
            ).update(
                current_progress=data_impacts["data_tasklog"]["current_progress"],
                completed_at=timezone.now().date()
                if data_impacts["data_tasklog"]["completed"]
                else None,
            )

        if data_impacts["gamestat"]:
            # Consider: percent interest streak
            poin_type = data_impacts["data_gamestat"]["reward_poin_type"]
            poin_value = data_impacts["data_gamestat"]["reward_poin_value"]
            kwargs = {
                poin_type: F(poin_type)
                + poin_value
                + (F("streak_percent_interest") * poin_value / 100)
            }
            GameStat.objects.filter(user_id=user_instance.id).update(**kwargs)

    @staticmethod
    def get_tasklog_instances(user_instance):
        tasklog_instances = TaskLog.objects.values(
            "id",
            "task_id__id",
            "task_id__activity_category",
            "task_id__reward_poin_type",
            "task_id__reward_poin_value",
            "task_id__target_unit",
            "task_id__target_value",
            "current_progress",
            "completed_at",
        ).filter(user_id=user_instance.id, created_at=timezone.now().date())
        return tasklog_instances

    @staticmethod
    def get_list_tasklog(user_instance):
        list_tasklog = UserActivityFinishSerializer.get_tasklog_instances(user_instance)
        if len(list_tasklog) == 0:
            # Condition if user access activity page w/o through homepage
            tasks_instances = Task.objects.all()
            tasklog_instances = [
                TaskLog(
                    user_id=user_instance,
                    task_id=task,
                    current_progress=0,
                    created_at=timezone.now().date(),
                )
                for task in tasks_instances
            ]
            TaskLog.objects.bulk_create(objs=tasklog_instances)
            list_tasklog = UserActivityFinishSerializer.get_tasklog_instances(
                user_instance
            )

        return list_tasklog

    def update(self, instance, validated_data):
        # 1) Get detail activity log
        try:
            activity_log = self.Meta.model.objects.values(
                "id", "track", "activity_id__category", "play_at"
            ).get(
                user_id=instance.id,
                activity_id=validated_data.get("activity_id"),
                finished=False,
            )
            str_track = str(activity_log["track"]).strip("'<>() ").replace("'", '"')
            dict_track = json.loads(str_track)

            if dict_track["type"] != "POSE" and dict_track["type"] != "AUDIO":
                raise ValueError

            (target,) = dict_track["data"].values()
        except self.Meta.model.DoesNotExist:
            raise ParseError("Request contains malformed data")
        except (ValueError, KeyError):
            raise serializers.ValidationError("Failed load track data")

        # 2) Count remain time and determine either finish or not
        now = timezone.now()
        finish_time = activity_log["play_at"] + timezone.timedelta(
            seconds=target["goals"]
        )

        finished = False
        target["current"] = (now - activity_log["play_at"]).total_seconds()
        remain_time = (finish_time - now).total_seconds()
        if now >= finish_time:
            finished = True
            target["current"] = target["goals"]
            remain_time = 0

        # 3) Update activitylog either the answer true or false
        self.Meta.model.objects.filter(id=activity_log["id"]).update(
            finished=finished,
            finish_at=timezone.now() if finished else None,
            track=json.dumps(
                {
                    "type": dict_track["type"],
                    "data": {"target": target},
                }
            ),
        )

        # 4) Impact if finish
        if finished:
            # Domino effect: finish => task done? => change gamestat
            list_tasklog = UserActivityFinishSerializer.get_list_tasklog(instance)
            UserActivityFinishSerializer.do_impacts(
                instance,
                list_tasklog,
                activity_log["activity_id__category"],
                target["goals"],
            )

        instance_activity_log = self.Meta.model(id=activity_log["id"])
        setattr(instance_activity_log, "activity_remain_time", remain_time)
        setattr(instance_activity_log, "activity_finished", finished)
        return instance_activity_log


class UserActivityQuizSerializer(serializers.ModelSerializer):
    # Schema of request body [PUT]
    # {
    #     "activity_id": "123y3hu13-ij12hi312hu",
    #     "activity_quiz": {
    #         "id": 1,
    #         "answer": "A"
    #     }
    # }

    # Schema of response
    # If the page refresh then user must be play again (reset track data)
    # {
    #     "activity_finished": True,
    #     "activity_quiz": {
    #         "id": 1,
    #         "answer": "A"
    #     }
    #     "answer_status": True
    # }
    activity_id = serializers.UUIDField(write_only=True, required=True)
    activity_quiz = serializers.DictField(required=True)
    activity_finished = serializers.BooleanField(read_only=True)
    answer_status = serializers.BooleanField(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["activity_id", "activity_quiz", "activity_finished", "answer_status"]

    def validate(self, data):
        try:
            activity_quiz_schema = Schema(
                {
                    "id": And(int, lambda i: i > 0),
                    "answer": And(str, lambda s: s in ("A", "B", "C", "D")),
                }
            )
            data["activity_quiz"] = Schema(activity_quiz_schema).validate(
                data["activity_quiz"]
            )
        except SchemaError:
            raise serializers.ValidationError("Invalid activity_quiz schema")
        return data

    def update(self, instance, validated_data):
        # 1) Get detail activitylog (reject if not reading activity)
        try:
            activity_log = self.Meta.model.objects.values(
                "id", "track", "activity_id__category"
            ).get(
                user_id=instance.id,
                activity_id=validated_data.get("activity_id"),
                finished=False,
            )

            str_track = str(activity_log["track"]).strip("'<>() ").replace("'", '"')
            dict_track = json.loads(str_track)

            if dict_track["type"] != "READ":
                raise ValueError
            target, attempt, secret_key, logs = dict_track["data"].values()

            # Extract answer key
            str_secret_key = base64.b64decode(secret_key)
            dict_secret_key = json.loads(str_secret_key.decode("utf-8"))

            user_ans = validated_data.get("activity_quiz")
            answer_status = user_ans["answer"] == dict_secret_key[f"{user_ans['id']}"]
        except self.Meta.model.DoesNotExist:
            raise ParseError("Request contains malformed data")
        except (ValueError, KeyError):
            raise serializers.ValidationError("Failed load track data")

        # 2) Check user answer
        if str(user_ans["id"]) in logs.keys():
            # Reject if already answered
            raise serializers.ValidationError("Question already answered")

        # Force to finish condition:
        # - Reach max attempt
        # - Length logs reach target goals
        finished = False
        if answer_status:
            logs[user_ans["id"]] = 1
            target["current"] += 1
        else:
            logs[user_ans["id"]] = 0
            attempt["current"] += 1
            if attempt["current"] == attempt["max"]:
                finished = True
        if len(logs) == target["goals"]:
            finished = True

        # 3) Update activitylog either the answer true or false
        self.Meta.model.objects.filter(id=activity_log["id"]).update(
            finished=finished,
            finish_at=timezone.now() if finished else None,
            track=json.dumps(
                {
                    "type": dict_track["type"],
                    "data": {
                        "target": target,
                        "attempt": attempt,
                        "secret_key": secret_key,
                        "logs": logs,
                    },
                }
            ),
        )

        if finished:
            # Domino effect: finish => task done? => change gamestat
            list_tasklog = UserActivityFinishSerializer.get_list_tasklog(instance)
            # 4) Impact for task and gamestat if the related task is done
            UserActivityFinishSerializer.do_impacts(
                instance,
                list_tasklog,
                activity_log["activity_id__category"],
                target["current"],
            )

        # 5) Setup response
        instance_activity_log = self.Meta.model(id=activity_log["id"])
        setattr(instance_activity_log, "activity_quiz", user_ans)
        setattr(instance_activity_log, "activity_finished", finished)
        setattr(instance_activity_log, "answer_status", answer_status)
        return instance_activity_log


class UserStreakTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCheck
        fields = ["streak_status", "date_target"]


class UserTaskTrackSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        read_only=True, source="task_id__activity_category"
    )

    class Meta:
        model = TaskLog
        fields = ["category", "completed_at"]
