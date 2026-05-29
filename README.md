# Insight Engine

This is a Python microservice that I worked on as part of backend and DevOps tasks. It is based on a Connexion API template and used for handling APIs, data processing, and integrations inside the system.

---

## What this project does

* Provides REST API endpoints
* Handles data processing and logging
* Connects with PostgreSQL and Kafka
* Supports monitoring (Prometheus, logging, etc.)
* Uses configuration-based setup

---

## Project Structure

The project is organized like this:

```id="o3y3qj"
config/           # configuration files
deploy/           # Kubernetes deployment configs
docs/             # documentation
evaluation/       # evaluation logic
explainability/   # model explainability (graphs, etc.)
model/            # model-related code
retraining/       # retraining pipeline

src/
  insight_engine/
    app.py
    config.py
    middleware/
    endpoints/
    domain/
    persistence/
    util/
    openapi/

test/             # unit tests
```

---

## How to run the project

Install dependencies:

```bash id="3r4nzt"
poetry install
```

Run the service:

```bash id="6bb5fp"
poetry run python -m insight_engine.app
```

---

## Running tests

```bash id="jlhh2k"
poetry run pytest
```

---

## Deployment

Deployment configs are available in the `deploy/` folder.

Service name used in deployment:

```id="y1n1qe"
insight-engine
```

---

## Important Notes

* Python package name: `insight_engine`
* Deployment name: `insight-engine`
* Environment variables use prefix: `INSIGHT_ENGINE_`

---

## What I did in this project

* Fixed all template placeholder issues across the project
* Renamed service from `my_service` to `insight_engine`
* Updated imports, configs, and test files
* Fixed CI/CD pipeline issues
* Ensured all tests and pipeline stages are passing

---

## Status

Project is working
Tests are passing
Pipeline is green
Ready for deployment
