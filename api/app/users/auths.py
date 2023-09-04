import datetime
import uuid

import jwt
from django.conf import settings
from rest_framework import authentication, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .models import User

# https://www.django-rest-framework.org/api-guide/authentication/#example


class JWTHandler:
    def __init__(self):
        self.credential = {}
        self.access_token_lifetime = settings.ACCESS_TOKEN_LIFETIME
        self.refresh_token_lifetime = settings.REFRESH_TOKEN_LIFETIME
        self.key_token = settings.KEY_TOKEN
        self.algorithm_token = settings.ALGORITHM_TOKEN

    def set_credential(self, credential):
        self.credential = credential

    def get_payload(self, lifetime):
        # https://pyjwt.readthedocs.io/en/latest/usage.html#registered-claim-names
        # exp & iat are default claims that auto detect expire when decode
        if not self.credential:
            raise jwt.exceptions.InvalidTokenError("Missing credential data!")
        iat = datetime.datetime.utcnow()
        return {**self.credential, "iat": iat, "exp": iat + lifetime}

    def encode(self, payload):
        return jwt.encode(
            payload=payload, key=self.key_token, algorithm=self.algorithm_token
        )

    def decode(self, token):
        try:
            payload = jwt.decode(
                jwt=token, key=self.key_token, algorithms=self.algorithm_token
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token")
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        return payload

    def get_access_token(self):
        payload = self.get_payload(self.access_token_lifetime)
        return self.encode(payload)

    def get_refresh_token(self):
        payload = self.get_payload(self.refresh_token_lifetime)
        return self.encode(payload)

    def get_httpresponse_init_jwt(self):
        response = Response()
        response.set_cookie(
            key=settings.COOKIES_NAME,
            value=self.get_refresh_token(),
            max_age=settings.COOKIES_REFRESH_TOKEN["LIFETIME"],
            secure=settings.COOKIES_REFRESH_TOKEN["SECURE"],
            samesite=settings.COOKIES_REFRESH_TOKEN["SAMESITE"],
            httponly=settings.COOKIES_REFRESH_TOKEN["HTTPONLY"],
            domain=settings.COOKIES_REFRESH_TOKEN["DOMAIN"],
        )
        response.data = {"jwt": self.get_access_token()}
        response.status = status.HTTP_200_OK
        return response

    def get_httpresponse_revoke_jwt(self):
        response = Response()
        response.delete_cookie(settings.COOKIES_NAME)
        response.data = {
            "deleted-refresh": True,
        }
        response.status = status.HTTP_200_OK
        return response


class JWTAuthentication(authentication.BaseAuthentication):
    def refresh_access_token(self, request):
        token = request.COOKIES.get(settings.COOKIES_NAME)
        if not token:
            raise AuthenticationFailed("Unauthentication")

        jwt_handler = JWTHandler()
        payload = jwt_handler.decode(token=token)
        jwt_handler.set_credential({"id": payload["id"]})
        return jwt_handler.get_access_token()

    def validate_access_token(self, request):
        # Frontend-note: if auth failed [only if invalid token]
        # Then delete access token from localstorage
        try:
            bearer_token = request.META.get("HTTP_AUTHORIZATION").split(" ")
            if len(bearer_token) >= 1 and bearer_token[0] == "Bearer":
                token = bearer_token[1]
            else:
                raise ValueError
        except Exception:
            raise AuthenticationFailed("Unauthentication")

        jwt_handler = JWTHandler()
        payload = jwt_handler.decode(token=token)
        return payload

    def authenticate(self, request):
        payload = self.validate_access_token(request=request)

        try:
            id = uuid.UUID(payload["id"])
            user = User.objects.get(id=id)
        except ValueError:
            raise AuthenticationFailed("Invalid payload token")
        except User.DoesNotExist:
            raise AuthenticationFailed("User doesn't exist")
        return (user, None)
