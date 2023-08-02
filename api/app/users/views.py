from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .auths import JWTAuthentication, JWTHandler
from .models import User
from .permissions import EmailValidatedPermission
from .serializers import LoginUserSerializer, RegisterUserSerializer


class RegisterView(APIView):
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            jwt_handler = JWTHandler()
            jwt_handler.set_credential({"id": str(serializer.data["id"])})
            response = jwt_handler.get_httpresponse_init_jwt()
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    throttle_scope = "login"

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(
                "Sorry, that email doesn't exist. Please try again."
            )

        if not user.check_password(password):
            raise AuthenticationFailed(
                "Sorry, that password isn't right. Please try again."
            )
        serializer = LoginUserSerializer(user)
        jwt_handler = JWTHandler()
        jwt_handler.set_credential({"id": str(serializer.data["id"])})
        response = jwt_handler.get_httpresponse_init_jwt()
        return response


class LogoutView(APIView):
    # Should be not throttling
    def get(self, request):
        token = request.COOKIES.get("jwt")
        if not token:
            raise AuthenticationFailed("Unauthentication")

        jwt_handler = JWTHandler()
        response = jwt_handler.get_httpresponse_revoke_jwt()
        return response


class ValidateAccessTokenView(APIView):
    # Should be not throttling
    def get(self, request):
        jwt_auth = JWTAuthentication()
        payload = jwt_auth.validate_access_token(request=request)
        return Response(payload, status=status.HTTP_200_OK)


class RefreshAccessTokenView(APIView):
    # Should be not throttling
    def get(self, request):
        jwt_auth = JWTAuthentication()
        new_access_token = jwt_auth.refresh_access_token(request=request)
        return Response({"jwt": new_access_token}, status=status.HTTP_200_OK)


class PasswordResetView:
    pass


class PasswordResetConfirmView:
    pass


class UserMeTrackerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [EmailValidatedPermission]

    def get(self, request):
        return Response({"message": "it was permitted"}, status=status.HTTP_200_OK)
