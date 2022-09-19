FROM python:3.10

COPY ./opt/req.txt /var/req.txt

WORKDIR /opt
COPY ./opt .
RUN pip install -r /var/req.txt

RUN chmod +x start.sh