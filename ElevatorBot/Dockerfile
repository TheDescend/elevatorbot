FROM python:3.9

COPY requirements.txt /ElevatorBot/requirements.txt

RUN pip3.9 install -r /ElevatorBot/requirements.txt

COPY ./ /ElevatorBot

WORKDIR /ElevatorBot

CMD python3.9 elevator.py