FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install nodemon
RUN apt-get update && apt-get upgrade -y && apt-get install -y nodejs npm
RUN npm install -g nodemon

# Prep Elevator Code
WORKDIR /app/ElevatorBot

COPY requirements.txt .

RUN pip3.9 install -r requirements.txt

COPY . .

CMD nodemon elevator.py
