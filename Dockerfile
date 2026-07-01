<<<<<<< HEAD
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
# Base image
FROM python:3.12-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Poetry stage
FROM python-base AS poetry

WORKDIR /opt

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev libffi-dev librdkafka-dev && \
    pip install poetry==1.8.4 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --without dev --no-root


# Runtime stage (IMPORTANT)
FROM python-base AS runtime

WORKDIR /app

EXPOSE 8080

# Copy dependencies from poetry stage
COPY --from=poetry /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=poetry /usr/local/bin /usr/local/bin

# Install runtime system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY config config
COPY src src

# Run the API
CMD ["uvicorn", "--factory", "insight_engine.app:create_app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]
>>>>>>> 03ccc86d988fcde1fef1bd43af64c4dcb3fc3506
