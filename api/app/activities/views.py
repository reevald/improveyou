from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.response import Response
from users.auths import JWTAuthentication

from .models import ACTIVITY_CATEGORIES, Activity
from .serializers import ActivityDetailSerializer


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
