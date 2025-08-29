# Ultra-minimal Python image
FROM python:3.11-alpine

WORKDIR /app

# Install deps in single layer
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /root/.cache

# Copy app
COPY . .

# Environment
ENV AWS_REGION=eu-west-1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]