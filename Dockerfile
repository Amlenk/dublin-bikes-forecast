FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY templates ./templates
COPY model/artifacts ./model/artifacts

EXPOSE 7860

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
