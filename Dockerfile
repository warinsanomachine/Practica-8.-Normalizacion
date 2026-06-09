FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "/dev/null"]