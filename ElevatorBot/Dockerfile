FROM python:3.10

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# add the path to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/app"

# install the requirements
COPY ./ElevatorBot/requirements.txt /app/ElevatorBot/requirements.txt
RUN pip3.10 install -r /app/ElevatorBot/requirements.txt

# copy over the required files
COPY ./version.py /app/version.py
COPY ./settings.py /app/settings.py
COPY ./DestinyEnums /app/DestinyEnums
COPY ./NetworkingSchemas /app/NetworkingSchemas
COPY ./ElevatorBot /app/ElevatorBot

# start elevator
WORKDIR /app
CMD ["python3.10", "ElevatorBot/elevator.py"]
EXPOSE 8080
