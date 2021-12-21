FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install nodemon
RUN apt-get update && apt-get upgrade -y 
#&& apt-get install -y nodejs npm
#RUN npm install -g nodemon

# Prep Elevator Code
WORKDIR /app/

COPY requirements.txt .

RUN pip3.10 install -r requirements.txt

COPY . .

CMD python elevator.py
