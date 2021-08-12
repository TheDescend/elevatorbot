FROM python:3.9

COPY requirements.txt /Website/requirements.txt

RUN pip3.9 install -r /Website/requirements.txt

COPY ./ /Website

WORKDIR /Website

EXPOSE 80

CMD uwsgi oauth.ini