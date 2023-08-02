#!/bin/sh

if [ "$RUN_MIGRATIONS" = "yes" ]
then
    echo "Running migrations..."
    python manage.py migrate
fi

exec "$@"