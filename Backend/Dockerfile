FROM python:3.11

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# add the path to pythonpath
ENV PYTHONPATH="${PYTHONPATH}:/app"

# install the requirements
RUN pip3.11 install uvloop
RUN pip3.11 install psycopg2
COPY ./Backend/requirements.txt /app/Backend/requirements.txt
RUN pip3.11 install -r /app/Backend/requirements.txt

# copy over the required files
COPY ./settings.toml /app/settings.toml
COPY ./alembic.ini /app/alembic.ini
COPY ./Shared /app/Shared
COPY ./Backend /app/Backend

# start the backend
WORKDIR /app
CMD ["sh", "-c", "alembic upgrade head && uvicorn Backend.main:app --proxy-headers --host 0.0.0.0 --port ${BACKEND_PORT}"]
EXPOSE $BACKEND_PORT
