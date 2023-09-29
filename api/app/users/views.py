from activities.models import ACTIVITY_CATEGORIES
from django.contrib.auth.models import update_last_login
from django.db import DatabaseError, transaction
from django.utils import timezone
from items.models import Item, Reward
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError
from rest_framework.response import Response
from tasks.models import Task

from .auths import JWTAuthentication, JWTHandler
from .models import (
    Bag,
    DailyCheck,
    DailyCheckQuestion,
    EventReward,
    GameStat,
    Object,
    TaskLog,
    User,
)
from .serializers import (
    LoginUserSerializer,
    RegisterUserSerializer,
    UserActivityFinishSerializer,
    UserActivityQuizSerializer,
    UserActivityStartSerializer,
    UserBagEquipItemSerializer,
    UserBagItemSerializer,
    UserBagUnequipItemSerializer,
    UserChangePublicitySerializer,
    UserChangeUsernameSerializer,
    UserDailyCheckQuestionSerializer,
    UserDailyCheckSerializer,
    UserEventRewardSerializer,
    UserGameStatSerializer,
    UserLeaderboardSerializer,
    UserObjectLeaderboardSerializer,
    UserObjectSerializer,
    UserStreakTrackSerializer,
    UserTaskProgressSerializer,
    UserTaskTrackSerializer,
)


class RegisterView(APIView):
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Initilization data of object and gamestat
            obj = Object(
                user_id=User(**serializer.data),
                character_id=None,
                hat_id=None,
                clothes_id=None,
                shoes_id=None,
            )
            stat = GameStat(
                user_id=User(**serializer.data),
            )
            obj.save()
            stat.save()
            jwt_handler = JWTHandler()
            jwt_handler.set_credential({"id": str(serializer.data["id"])})
            response = jwt_handler.get_httpresponse_init_jwt()
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    throttle_scope = "login/logout"

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            jwt_handler = JWTHandler()
            update_last_login(None, user)
            jwt_handler.set_credential({"id": str(user.id)})
            return jwt_handler.get_httpresponse_init_jwt()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    throttle_scope = "login/logout"

    def get(self, request):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthentication")

        jwt_handler = JWTHandler()
        response = jwt_handler.get_httpresponse_revoke_jwt()
        return response


class ValidateAccessTokenView(APIView):
    throttle_scope = "jwt:refresh/validate"

    def get(self, request):
        jwt_auth = JWTAuthentication()
        payload = jwt_auth.validate_access_token(request=request)
        return Response(payload, status=status.HTTP_200_OK)


class RefreshAccessTokenView(APIView):
    throttle_scope = "jwt:refresh/validate"

    def get(self, request):
        jwt_auth = JWTAuthentication()
        new_access_token = jwt_auth.refresh_access_token(request=request)
        return Response({"jwt": new_access_token}, status=status.HTTP_200_OK)


class PasswordResetView:
    pass


class PasswordResetConfirmView:
    pass


class UserMeObjectView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user_object = Object.objects.values(
                "character_id",
                "hat_id",
                "clothes_id",
                "shoes_id",
                "background_id",
                "character_id__sprite_path",
                "hat_id__sprite_path",
                "clothes_id__sprite_path",
                "shoes_id__sprite_path",
                "background_id__sprite_path",
            ).get(user_id=self.request.user.id)
        except Object.DoesNotExist:
            raise ParseError("Request contains malformed data")
        serializer = UserObjectSerializer(user_object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeGameStatView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user_gamestat = GameStat.objects.values(
                "user_id__username",
                "gold",
                "poin_brain",
                "poin_heart",
                "poin_muscle",
                "streak_current",
                "streak_percent_interest",
            ).get(user_id=self.request.user.id)
        except GameStat.DoesNotExist:
            raise ParseError("Request contains malformed data")
        serializer = UserGameStatSerializer(user_gamestat)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeChangeUsernameView(APIView):
    throttle_scope = "change_username"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserChangeUsernameSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeChangePublicityView(APIView):
    throttle_scope = "change_publicity"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserChangePublicitySerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeBagItemView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        serializer = UserBagItemSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeBagEquipItemView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserBagEquipItemSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeBagUnequipItemView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserBagUnequipItemSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeDailyCheckView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        instance = DailyCheckQuestion.objects.filter(availability=True)
        serializer = UserDailyCheckQuestionSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserDailyCheckSerializer(
            data=request.data, context={"user": self.request.user}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeTaskProgressView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get_tasklog_instances(self):
        tasklog_instances = TaskLog.objects.values(
            "task_id__id",
            "task_id__activity_category",
            "task_id__name",
            "task_id__reward_poin_type",
            "task_id__reward_poin_value",
            "task_id__target_type",
            "task_id__target_value",
            "task_id__target_unit",
            "current_progress",
            "completed_at",
        ).filter(user_id=self.request.user.id, created_at=timezone.now().date())

        return tasklog_instances

    def get(self, request):
        tasklog_instances = self.get_tasklog_instances()
        if len(tasklog_instances) == 0:
            # If task log haven't created (one day = one log for each task)
            # 1) Get list task
            tasks_instances = Task.objects.all()
            # 2) Create tasklog for each task
            tasklog_instances = [
                TaskLog(
                    user_id=self.request.user,
                    task_id=task,
                    current_progress=0,
                    created_at=timezone.now().date(),
                )
                for task in tasks_instances
            ]

            TaskLog.objects.bulk_create(objs=tasklog_instances)

            tasklog_instances = self.get_tasklog_instances()
        serializer = UserTaskProgressSerializer(tasklog_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeEventRewardView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Note:
        # Event will be handled by admin (human in the loop)
        # EventReward will be handled by system (scheduler) or admin

        # 1) Check that user have rewards in event_reward table
        list_event_id = EventReward.objects.values("event_id", "event_id__name").filter(
            user_id=self.request.user, rewards_claimed_at__isnull=True
        )

        if len(list_event_id) == 0:
            return Response([], status=status.HTTP_200_OK)

        # 2) Check if reward available in event
        list_item_id = Reward.objects.values("item_id", "event_id").filter(
            event_id__in=[data["event_id"] for data in list_event_id]
        )

        if len(list_item_id) == 0:
            return Response([], status=status.HTTP_200_OK)

        data_event = {
            dict_event["event_id"]: {"event_name": dict_event["event_id__name"]}
            for dict_event in list_event_id
        }

        data_reward_event = {
            dict_reward["item_id"]: {"event_id": dict_reward["event_id"]}
            for dict_reward in list_item_id
        }

        new_bag_item = [
            Bag(
                user_id=self.request.user,
                item_id=Item(id=data["item_id"]),
                source_type="event",
            )
            for data in list_item_id
        ]

        try:
            with transaction.atomic():
                # 3) Insert rewards into bag
                # Ignore conflict when duplicate unique pair (item_id and user_id)
                # Only insert real new items that user haven't these yet
                Bag.objects.bulk_create(new_bag_item, ignore_conflicts=True)
                # 4) Update date rewards_claimed_at
                EventReward.objects.filter(
                    user_id=self.request.user, rewards_claimed_at__isnull=True
                ).update(rewards_claimed_at=timezone.now())
        except DatabaseError:
            raise ValidationError("Failed to claim rewards or save rewards into bag")

        # Since there is limitation return of bulk_create (can't return all fields)
        # We need to select Items manually
        # https://stackoverflow.com/a/39314124
        item_instances = Item.objects.filter(
            pk__in=[data["item_id"] for data in list_item_id]
        )

        for item_instance in item_instances:
            event_id = data_reward_event[item_instance.id]["event_id"]
            event_name = data_event[event_id]["event_name"]
            setattr(item_instance, "event__id", event_id)
            setattr(item_instance, "event__name", event_name)

        serializer = UserEventRewardSerializer(item_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeActivityStartView(APIView):
    throttle_scope = "resources_activity"
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = UserActivityStartSerializer(
            data=request.data, context={"user": self.request.user}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeActivityQuizView(APIView):
    throttle_scope = "resources_activity"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserActivityQuizSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeActivityFinishView(APIView):
    throttle_scope = "resources_activity"
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        serializer = UserActivityFinishSerializer(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeTrackerView(APIView):
    authentication_classes = [JWTAuthentication]

    # TODO: plan to create new field for "best streak" instead count manual
    def get(self, request):
        streak_track = (
            DailyCheck.objects.values("streak_status", "date_target")
            .filter(user_id=self.request.user.id)
            .order_by("-created_at")
        )

        task_track = (
            TaskLog.objects.values("task_id__activity_category", "completed_at")
            .filter(user_id=self.request.user.id, completed_at__isnull=False)
            .order_by("-created_at")
        )

        serializer_streak = UserStreakTrackSerializer(streak_track, many=True)
        serializer_track = UserTaskTrackSerializer(task_track, many=True)
        return Response(
            {
                "date_joined": self.request.user.date_joined,
                "streak_track": serializer_streak.data,
                "task_track": serializer_track.data,
            },
            status=status.HTTP_200_OK,
        )


class LeaderboardAPI(APIView):
    throttle_scope = "resources_leaderboard"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        NUM_TOP_LEADERBOARD = 10
        category = request.GET.get("category", None)
        activity_categories = [cat[0] for cat in ACTIVITY_CATEGORIES]
        if category and category not in activity_categories:
            raise AuthenticationFailed("Invalid category")

        categories = activity_categories if not category else [category]
        leaderboards = []
        for cat in categories:
            poin_type = ""
            if cat == "exercise":
                poin_type = "poin_muscle"
            if cat == "meditation":
                poin_type = "poin_heart"
            if cat == "reading":
                poin_type = "poin_brain"

            leaderboard = GameStat.objects.values(
                "user_id__username", "user_id", poin_type
            ).order_by(f"-{poin_type}")[:NUM_TOP_LEADERBOARD]
            leaderboards.extend(leaderboard)

        # Remove duplicate user
        list_user_id = []
        for data in leaderboards:
            if data["user_id"] not in list_user_id:
                list_user_id.append(data["user_id"])

        data_objects = Object.objects.values(
            "user_id",
            "character_id__sprite_path",
            "hat_id__sprite_path",
            "clothes_id__sprite_path",
            "shoes_id__sprite_path",
            "background_id__sprite_path",
        ).filter(user_id__in=list_user_id)

        # Frontend note: need to preprocessing to match between gamestat and object
        serializer_object = UserObjectLeaderboardSerializer(data_objects, many=True)
        serializer_leaderboards = UserLeaderboardSerializer(leaderboards, many=True)
        return Response(
            {
                "leaderboard_data": serializer_leaderboards.data,
                "leaderboard_object": serializer_object.data,
            },
            status=status.HTTP_200_OK,
        )
