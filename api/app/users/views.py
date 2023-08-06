from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.response import Response

from .auths import JWTAuthentication, JWTHandler
from .models import GameStat, Object, User
from .permissions import EmailValidatedPermission
from .serializers import (
    LoginUserSerializer,
    RegisterUserSerializer,
    UserBagItemSerializer,
    UserChangePublicitySerializer,
    UserChangeUsernameSerializer,
    UserGameStatSerializer,
    UserObjectSerializer,
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
            user_object = Object.objects.get(user_id=self.request.user.id)
        except Object.DoesNotExist:
            raise ParseError("Request contains malformed data")
        serializer = UserObjectSerializer(user_object)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeGameStatView(APIView):
    throttle_scope = "resources_home"
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user_gamestat = GameStat.objects.get(user_id=self.request.user.id)
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


class UserMeTrackerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [EmailValidatedPermission]

    def get(self, request):
        return Response({"message": "it was permitted"}, status=status.HTTP_200_OK)
