"""
Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "static/"

# Cookie-JWT
# https://docs.djangoproject.com/en/4.2/ref/request-response/#django.http.HttpResponse.set_cookie
COOKIES_REFRESH_TOKEN = {
    "LIFETIME": REFRESH_TOKEN_LIFETIME,  # From base settings
    "SECURE": False,  # Not safe
    "HTTPONLY": True,
    "SAMESITE": "None",  # Not safe
}

REST_FRAMEWORK = {
    # Only return in JSON format
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",  # Not good for production
    ],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "register": "10/hour",
        "login/logout": "10/hour",
        "jwt:refresh/validate": "5/hour",
        "resources_home": "720/hour",
        "resources_activity": "720/hour",
        "resources_leaderboard": "720/hour",
        "change_username": "15/day",
        "change_publicity": "60/hour",
        "buy_item": "30/hour",
    },
}

# CORS
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOW_ALL_ORIGINS = True  # Not good for productions
CORS_ALLOW_CREDENTIALS = True  # Cookies

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
