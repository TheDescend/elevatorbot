FROM python:3.9

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /ElevatorBot/requirements.txt

RUN pip3.9 install -r /ElevatorBot/requirements.txt

COPY ./ /ElevatorBot

WORKDIR /ElevatorBot

CMD python elevator.py