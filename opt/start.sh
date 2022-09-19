#!/bin/sh
python3 habr/manage.py migrate
python3 habr/manage.py createsuperuser --no-input --username max --email maxf39@mail.ru
nohup python3 habr/manage.py runserver 0.0.0.0:8000 > django.out &
nohup python3 parser/main.py > parser.out &
