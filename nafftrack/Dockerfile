# pull the official docker image
FROM python:3.10-slim AS builder

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN apt update
RUN apt install -y git
RUN pip install --upgrade pip
COPY example/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt



# pull official base image
FROM python:3.10-slim AS final

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/discord_bot
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY example/ $APP_HOME
COPY nafftrack/ $APP_HOME/nafftrack

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app
