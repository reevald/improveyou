from django.conf import settings
from itsdangerous import URLSafeTimedSerializer
from rest_framework.exceptions import AuthenticationFailed


def generate_magic_link(token, event):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps([token, event], salt=settings.VERIFY_MAGIC_LINK_SALT)


def verify_magic_link(magic_link):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        token, event = serializer.loads(
            magic_link,
            salt=settings.VERIFY_MAGIC_LINK_SALT,
            max_age=settings.VERIFY_MAGIC_LINK_LIFETIME,
        )
    except Exception:
        raise AuthenticationFailed("Invalid magic link")
    return token, event
