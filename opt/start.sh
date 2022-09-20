#!/bin/sh
#python3 habr/manage.py migrate
#python3 habr/manage.py createsuperuser --no-input --username max --email maxf39@mail.ru
nohup python3 -u habr/manage.py runserver 0.0.0.0:8000 >> django.out 2>&1 &
nohup python3 -u parser/main.py >> parser.out 2>&1 &
while true; do sleep 10000; done