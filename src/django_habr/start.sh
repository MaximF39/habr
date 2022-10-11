#!/bin/sh

python manage.py makemigrations --no-input
python manage.py migrate --fake sessions zero
python manage.py migrate --fake-initial
python manage.py collectstatic --no-input
python manage.py createsuperuser --no-input
gunicorn django_habr.wsgi:application -c gunicorn.conf.py

