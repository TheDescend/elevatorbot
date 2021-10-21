FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /app/Website

COPY requirements.txt .

RUN pip3.9 install -r get_requirements.txt

COPY . .

EXPOSE 80

CMD uwsgi oauth.ini
