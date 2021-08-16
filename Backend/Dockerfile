FROM winnerokay/uvicorn-gunicorn:python3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt .

RUN pip3.9 install -r requirements.txt

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port 80 --reload