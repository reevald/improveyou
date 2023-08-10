from activities.models import Recommendation
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.response import Response
from users.auths import JWTAuthentication
from users.models import RecommendationLog

from .models import ACTIVITY_CATEGORIES, Activity
from .serializers import (
    ActivityDetailSerializer,
    ActivityRecommendationSerializer,
    ActivitySerializer,
)


class ActivityDetailView(APIView):
    throttle_scope = "resources_activity"
    authentication_classes = [JWTAuthentication]

    def get(self, request, category, slug):
        if category not in [cat[0] for cat in ACTIVITY_CATEGORIES]:
            raise AuthenticationFailed("Invalid category")

        try:
            activity = Activity.objects.get(category=category, slug=slug)
        except Activity.DoesNotExist:
            raise ParseError("Request contains malformed data")
        serializer = ActivityDetailSerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivitiesWithRecommendationView(APIView):
    throttle_scope = "resources_activity"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Params [optional]: category, offset & limit
        # Limit (default=10 activity each category, max=100)
        category = request.GET.get("category", None)
        activity_categories = [cat[0] for cat in ACTIVITY_CATEGORIES]
        if category and category not in activity_categories:
            raise AuthenticationFailed("Invalid category")

        try:
            limit = abs(int(request.GET.get("limit", 10)))
            offset = abs(int(request.GET.get("offset", 0)))
            if offset >= limit or limit - offset > 100:
                # Max number data each category 100 (prevent too much request)
                raise ValueError
        except ValueError:
            raise ParseError("Invalid limit or offset")

        # Always using latest recommendation to prevent error predict service
        # these will more relate with user condition as well (near today)
        try:
            recom_urge_level = (
                RecommendationLog.objects.values("urge_level")
                .filter(user_id=self.request.user.id)
                .latest("issue_at")
            )
        except RecommendationLog.DoesNotExist:
            # Since the behaviour filter + latest similar with get then
            # Important to check if exist or not
            # If not exist (caused by cold start condition in ML)
            # Cold start: asume user in medium level
            recom_urge_level = {"urge_level": "medium"}

        list_recom_activities = Recommendation.objects.values(
            "activity_id",
            "activity_id__name",
            "activity_id__category",
            "activity_id__slug",
            "activity_id__thumbnail_path",
            "activity_id__created_at",
        ).filter(urge_level=recom_urge_level["urge_level"])

        categories = activity_categories if not category else [category]
        list_activities = []
        for cat in categories:
            activity = Activity.objects.values(
                "id", "category", "slug", "name", "thumbnail_path", "created_at"
            ).filter(category=cat)[offset:limit]
            list_activities.extend(activity)

        serializer_activities = ActivitySerializer(list_activities, many=True)
        serializer_recom_activities = ActivityRecommendationSerializer(
            list_recom_activities, many=True
        )
        return Response(
            {
                "recommendations": serializer_recom_activities.data,
                "activities": serializer_activities.data,
            },
            status=status.HTTP_200_OK,
        )
