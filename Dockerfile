FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

ENV FLASK_CONFIG=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# seed then run (seed is idempotent)
CMD ["sh", "-c", "python seed.py && gunicorn -b 0.0.0.0:8000 -w 2 'run:app'"]
