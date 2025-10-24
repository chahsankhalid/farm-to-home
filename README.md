# Repository <%my-service%> API

<% This is a template project. To begin, search for "<%...%>" and replace all occurrences with your input %>
<% Also rename the application module folder named "my_service"! %>

## Description

This is a Python Connexion microservice, hosting REST API endpoints to <%achieve your purpose%>.

The Connexion framework from Zalando is used because this framework allows API-driven development, making it easy to 
keep the API spec, documentation, and code in sync. Note that we use AsyncApp, which means the entire framework is 
asynchronous, and we do not use Flask at all. Older versions of Connexion (< 3) were tightly coupled with Flask, please
be aware there may be Q&A answers online (or AI answers) that assume Flask is still used.

## Local development

#### Folder structure

Here are the relevant folders and what they do.

* In `.` you can find the dependency definitions (`requirements.txt`) and CI/CD files.
* In `deploy` you can find files to deploy the service to Kubernetes, using our GitOps framework FluxCD. Some additional
  configuration is necessary in the repo `fluxcd-environments`.
* In the `config` folder, there are environment-specific configurations. They each inherit from `base.yaml`. The
  appropriate file is loaded based on the `FRAUDIO_ENV` environment variable. Overrides and secrets can be provided by
  a fixed prefix followed by the config key, e.g. `EXAMPLE_API_DEFAULT_LOG_LEVEL=error`.
* In `src` are all the Python sources required to run the API.
    * In `src/app.py` you can find Connexion bootstrapping logic.
    * In `src/config.py` loads the configuration and environment variables for the current environment. 
    * In `src/openapi` is the OpenAPI specification which acts simultaneously as a REST router.
    * In `src/util` you can find a few general programming utilities.
    * In `src/persistence` you can find database abstractions and migrations. Note that the `__init__.py` always 
      contains the current version, to which the framework automatically up/downgrades on application startup.
      With multiple API instances running, this means DB changes should be mostly backwards compatible and it's best
      to start new pods one by one.
    * In `src/serialization` you can find some configuration to automatically serialize Python objects to JSON.
    * In `src/middleware` is logic necessary for logging HTTP requests and responses to Kafka
    * In `src/endpoints` are the methods that directly serve incoming routes
    * In `src/domain` is the business logic behind endpoints
    * In `src/accesscontrol` is logic to check request credentials, provided by the separate Fraudio auth-service
* In `test` are all the Python sources required to test the API.
    * In `test/conftest.py` you can find the general test config and test scopes. This file name must stay the same by
      a framework convention.
    * In `test/test_config.py` you can find a unit test which tests if the application config is loaded correctly. This
      does not contain any configuration by itself.
    * In `test/run_all.py` is a simple way to run all tests.
    * In `test/test_api_*` you can find integration tests for API endpoints.
    * In `test/testutil` you can find setup code for test fixtures and utility functions.
    * In `test/testdata` you can find example requests and responses used in integration tests. The files are often
      named `*-request.json` and `*-response.json` to indicate if they are request bodies (for a POST) or response
      bodies (usually for a GET).

#### Running and testing the application

##### Setting up

The application is built with [python poetry](https://python-poetry.org/docs/)
In case you use IntelliJ-based IDEs(Idea/PyCharm),
you can find setup instructions on the [Jetbrains Website](https://www.jetbrains.com/help/idea/poetry.html#poetry-env)

⚠️ Make sure you run the following commands before you start⚠️

```shell
poetry config http-basic.fraudioInternalRepo "Private-Token" "<your-private-token>" 
poetry update
```

##### Unit vs Integration testing

If you are in doubt what kind of test to write: for small
applications, prefer integration tests (i.e. calling the API) for happy flows,
unit tests for edge cases.

For examples, see `test_api.py` (integration test) and
`test_config.py` (unit test).

##### Running tests

We are using `pytest` because it works well with this framework.
Test fixtures allows us to initialize an app environment for
integration testing. Fixtures and other configuration are
defined in `conftest.py`. This filename is a recommended
default and should not be changed.

file `.env.sample` contains environment variables, required for application run.
You may use a tool like [direnv](https://direnv.net) to make things easier.

You can run the application in the command line by doing

```shell
poetry run app
```

You can run tests in the command line by doing

```shell
poetry run tests
```

If you want to run tests within a Docker container, execute the following command

```shell
docker build -f Dockerfile --build-arg GITLAB_TOKEN="$GITLAB_TOKEN" --build-arg GITLAB_TOKEN_NAME="Private-Token"\
   --target testing -t fraudio-local-api-test:0.1.0 . && \ 
docker run -it --rm --network=host fraudio-local-api-test:0.1.0 
```

if you want to run app as it runs on test/stg

```shell
docker build -f Dockerfile --build-arg GITLAB_TOKEN="$GITLAB_TOKEN" --build-arg GITLAB_TOKEN_NAME="Private-Token" \
   -t fraudio-local-api:0.1.0 . 
docker run -it  --rm -v "$KAFKA_SECRETS_PATH:/fraudio-local-api/.tls" -p8080:8080 -e FRAUDIO_ENV='TST' -eRUNNING_PLATFORM='local' -e KAFKA_SCHEMA_REGISTRY_PASSWORD=$KAFKA_SCHEMA_REGISTRY_PASSWORD -e FRAUDIO_KAFKA_ENABLED=false -e KAFKA_SECRETS_PATH="/fraudio-local-api/.tls"  fraudio-local-api:0.1.0
```

#### API specification

Have a look in `./src/openapi`. Here are the API specifications.
Each endpoint in this file specifies an `operationId`, which points
to a python method that should be executed when an HTTP request is accepted.
