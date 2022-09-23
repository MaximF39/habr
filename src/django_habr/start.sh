#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input
python manage.py createsuperuser --noinput
gunicorn django_habr.wsgi:application -c gunicorn.conf.py

