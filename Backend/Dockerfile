FROM kigstn/uvicorn-gunicorn-fastapi:python3.10-rc

ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt .

RUN pip3.10 install -r requirements.txt

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload