FROM kigstn/uvicorn-gunicorn-fastapi:python3.10.2

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# get arg from docker-compose, otherwise use default
ARG BACKEND_PORT=8070

# add the path to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/app"

# install the requirements
RUN pip3.10 install uvloop
COPY ./Backend/requirements.txt /app/Backend/requirements.txt
RUN pip3.10 install -r /app/Backend/requirements.txt

# copy over the required files
COPY ./settings.toml /app/settings.toml
COPY ./Shared /app/Shared
COPY ./Backend /app/Backend

# start the backend
WORKDIR /app
CMD ["sh", "-c", "uvicorn Backend.main:app --proxy-headers --host 0.0.0.0 --port ${BACKEND_PORT}"]
EXPOSE $BACKEND_PORT
