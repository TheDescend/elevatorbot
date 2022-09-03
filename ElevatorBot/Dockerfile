FROM python:3.10.3

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# add the path to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/app"

# install ffmpeg
RUN apt-get -y update
RUN apt-get -y install ffmpeg

# install the requirements
RUN pip3.10 install uvloop
COPY ./ElevatorBot/requirements.txt /app/ElevatorBot/requirements.txt
RUN pip3.10 install -r /app/ElevatorBot/requirements.txt

# copy over the required files
COPY ./version.py /app/version.py
COPY ./settings.toml /app/settings.toml
COPY ./Shared /app/Shared
COPY ./ElevatorBot /app/ElevatorBot
COPY ./nafftrack /app/nafftrack

# start elevator
WORKDIR /app
CMD ["python3.10", "ElevatorBot/elevator.py"]
EXPOSE $ELEVATOR_PORT
EXPOSE 8877
