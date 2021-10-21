FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install nodemon
RUN apt-_get update && apt-_get upgrade -y && apt-_get install -y nodejs npm
RUN npm install -g nodemon

# Prep Elevator Code
WORKDIR /app/ElevatorBot

COPY requirements.txt .

RUN pip3.10 install -r get_requirements.txt

COPY . .

CMD nodemon elevator.py
