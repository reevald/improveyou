#!/bin/bash
export DJANGO_SETTINGS_MODULE=config.django.settings.development

# Security
export SECRET_KEY="django-insecure-%%0$*jz!1t9-k2!a7!9gn0@88flk$b=1jj2x7)y6xdyhbhn#q="
export DJANGO_ALLOWED_HOSTS=*

# Database
export SQL_ENGINE=django.db.backends.mysql
export SQL_DATABASE=improveyoudb
export SQL_USER=root
export SQL_PASSWORD=
export SQL_HOST=127.0.0.1
export SQL_PORT=3306

# Caches
export CACHE_FILEBASED_LOCATION="/var/tmp/django_cache"

# Magic link
export VERIFY_MAGIC_LINK_SALT="django-insecure-*u6R5Q*zaBuphoTraprL"

# Admin
export ADMIN_URL="insecure-RnIzLTlGZThpaHU5QTllUCotSXhvVG9xbG0hX0lnT2NIaXdVYnJsYzBjNV9zODBVJHJpeSprYWZJcExTV2VyRQ==/"

# Container
export RUN_MIGRATIONS=yes