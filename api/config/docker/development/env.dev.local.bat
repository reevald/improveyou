set DJANGO_SETTINGS_MODULE=config.django.settings.development

REM Security
set "SECRET_KEY=django-insecure-%%0$*jz!1t9-k2!a7!9gn0@88flk$b=1jj2x7)y6xdyhbhn#q="
set DJANGO_ALLOWED_HOSTS=*

REM Database
set SQL_ENGINE=django.db.backends.mysql
set SQL_DATABASE=improveyoudb
set SQL_USER=root
set SQL_PASSWORD=rootpassword
set SQL_HOST=127.0.0.1
set SQL_PORT=3306

REM Caches
set "CACHE_FILEBASED_LOCATION=D:/Documents/AIC/improveyou/api/cache"

REM Magic link
set "VERIFY_MAGIC_LINK_SALT=django-insecure-*u6R5Q*zaBuphoTraprL"

REM Admin
set "ADMIN_URL=insecure-RnIzLTlGZThpaHU5QTllUCotSXhvVG9xbG0hX0lnT2NIaXdVYnJsYzBjNV9zODBVJHJpeSprYWZJcExTV2VyRQ==/"

REM Container
set RUN_MIGRATIONS=yes