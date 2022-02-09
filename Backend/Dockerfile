# todo change back on full release
# FROM kigstn/uvicorn-gunicorn-fastapi:python3.10.2
FROM python:3.10.2
RUN pip3.10 install uvicorn

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# add the path to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/app"

# install the requirements
# todo change back on full release
# RUN pip3.10 install uvloop
COPY ./Backend/requirements.txt /app/Backend/requirements.txt
RUN pip3.10 install -r /app/Backend/requirements.txt

# copy over the required files
COPY ./settings.toml /app/settings.toml
COPY ./Shared /app/Shared
COPY ./Backend /app/Backend

# start the backend
WORKDIR /app
CMD ["uvicorn", "Backend.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8070"]
EXPOSE 8070
