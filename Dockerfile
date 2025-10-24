FROM python:3.12-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=20 \
    POETRY_VERSION="1.8.4" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

FROM python-base AS poetry

ARG GITLAB_TOKEN
ARG GITLAB_TOKEN_NAME

ENV GITLAB_TOKEN=${GITLAB_TOKEN:-} \
    GITLAB_TOKEN_NAME=${GITLAB_TOKEN_NAME:-"Private-Token"}

WORKDIR /opt

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev libffi-dev librdkafka-dev && \
    pip install poetry==$POETRY_VERSION toml==0.10.2 && \
    mkdir -p /root/.config/pypoetry/ && \
    echo "[http-basic.fraudioInternalRepo]" > /root/.config/pypoetry/auth.toml && \
    echo "username = \"$GITLAB_TOKEN_NAME\"" >> /root/.config/pypoetry/auth.toml && \
    echo "password = \"$GITLAB_TOKEN\"" >> /root/.config/pypoetry/auth.toml && \
    poetry --version && \
    # Clean up APT cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# Copy project files and install dependencies
COPY pyproject.toml poetry.lock poetry_set_app_version.py VERSION ./
RUN python poetry_set_app_version.py && \
    poetry install --no-interaction -vvv --without dev --no-root --no-directory

FROM poetry AS poetry-test-config
RUN python poetry_set_app_version.py && \
    poetry install --no-interaction -vvv --only dev --no-root

FROM python-base AS testing

ENV APP_HOME="/app-home" \
    PATH="/usr/local/bin:$PATH"

WORKDIR $APP_HOME

# Copy installed dependencies from poetry-test-config
COPY --from=poetry-test-config /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY . ./

CMD poetry run tests

FROM python-base AS runtime

ENV APP_HOME="/app-home" \
    PATH="/usr/local/bin:$PATH"

WORKDIR $APP_HOME

EXPOSE 8080

# Copy installed dependencies from poetry stage
COPY --from=poetry /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=poetry /usr/local/bin /usr/local/bin

RUN apt-get update && \
    apt-get install -y --no-install-recommends librdkafka-dev && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir logs

COPY config config
COPY src src
COPY VERSION ./

CMD ["uvicorn", "--factory", "<%my-service%>.app:create_app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]
