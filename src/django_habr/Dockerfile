FROM python:3.10

RUN apt-get update
RUN apt-get -y install gunicorn

ARG USER
ARG PASSWORD
ARG DJANGO_PORT
ARG PATH_PROJECT

ENV USER=$USER
ENV PASSWORD=$PASSWORD
ENV DJANGO_PORT=$DJANGO_PORT
ENV PATH_PROJECT=$PATH_PROJECT

ENV VIRTUAL_ENV=$PATH_PROJECT/venv

RUN useradd -r $USER -p $PASSWORD

COPY . $PATH_PROJECT
WORKDIR $PATH_PROJECT

RUN python -m venv $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate
RUN pip install --upgrade pip
RUN pip install -r req.txt

RUN chmod +x ./start.sh
#RUN chmod -R 777 /static

#USER $USER

EXPOSE $DJANGO_PORT

ENTRYPOINT ["sh", "./start.sh"]

