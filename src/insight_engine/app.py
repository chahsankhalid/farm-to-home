import contextlib
import logging
import logging.config
from typing import AsyncIterator

import google.cloud.logging
from connexion import AsyncApp, ConnexionMiddleware
from connexion.middleware import MiddlewarePosition
from connexion.middleware.swagger_ui import SwaggerUIMiddleware
from connexion.options import SwaggerUIOptions
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from insight_engine import domain, endpoints
from insight_engine.config import AppConfig, ConfigLoader
from insight_engine.domain import models
from insight_engine.middleware.fraudio_middleware import FraudioMiddleware
from insight_engine.openapi import bundling
from insight_engine.persistence.kafka_streaming import kafka_streaming
from insight_engine.persistence.kafka_message_handler import handle_kafka_message
from insight_engine.serialization.custom_json_encoder import CustomJsonEncoder
from insight_engine.util import paths, yaml
from insight_engine.util.secrets import build_secrets_manager
from insight_engine.util.tracing import FraudioTracingSampler, trace_functions_in_module


def create_app() -> AsyncApp:
    config: AppConfig = ConfigLoader.get_instance()

    init_logging(config)
    logger = logging.getLogger(__name__)
    logger.info('Application logging configured.')

    logger.info(f'Starting application in environment {config.fraudio_env} ({config.fraudio_env_display_name}).')

    logger.debug('Initializing Connexion...')
    swagger_ui_options = SwaggerUIOptions(swagger_ui=config.openapi_ui, swagger_ui_path='/docs')
    middlewares = [
        middleware
        for middleware in ConnexionMiddleware.default_middlewares
        if middleware is not SwaggerUIMiddleware or config.openapi_ui
    ]
    cnx_app = AsyncApp(
        __name__,
        lifespan=lifespan_handler,
        middlewares=middlewares,
        jsonifier=CustomJsonEncoder(),
        swagger_ui_options=swagger_ui_options
    )

    if config.tracing_enabled:
        logger.debug('Setting up open telemetry...')
        set_global_textmap(TraceContextTextMapPropagator())
        # noinspection PyProtectedMember
        trace_sampler = ParentBased(root=FraudioTracingSampler(sampling._get_from_env_or_default()))
        trace.set_tracer_provider(TracerProvider(sampler=trace_sampler))
        span_processor = BatchSpanProcessor(OTLPSpanExporter())
        trace.get_tracer_provider().add_span_processor(span_processor)
        trace_functions_in_module(domain)
        trace_functions_in_module(models)
        trace_functions_in_module(endpoints)
        cnx_app.add_middleware(OpenTelemetryMiddleware, MiddlewarePosition.BEFORE_EXCEPTION)

    # Note that we do not call cnx_app.add_error_handler(Exception, errors.handle_api_exception).
    # Errors are handled by our middleware, so that we always have the finalized response available in the audit trail.
    logger.debug('Registering request hooks...')
    cnx_app.add_middleware(ProxyHeadersMiddleware, MiddlewarePosition.BEFORE_SECURITY, trusted_hosts=['*'])
    cnx_app.add_middleware(FraudioMiddleware, MiddlewarePosition.BEFORE_SECURITY)

    logger.debug('Initializing API routes and controllers...')
    spec_path = "openapi/api-spec.yaml"

    cnx_app.add_api(
         spec_path,
         strict_validation=True,
         validate_responses=True
     )

    kafka_enabled = config.fraudio_kafka_enabled
    if not kafka_enabled:
      logger.info('Kafka is disabled, all Kafka IO will be skipped.')

    logger.info('App initialization complete.')
    return cnx_app

@contextlib.asynccontextmanager
async def lifespan_handler(_: ConnexionMiddleware) -> AsyncIterator:
    logger = logging.getLogger(__name__)
    logger.info('App lifespan: setting up async features...')

    config = ConfigLoader.get_instance()

    if config.fraudio_kafka_enabled:
        logger.debug('Initializing Kafka streaming...')
        secret_manager = build_secrets_manager()

        await kafka_streaming.setup(
            secret_manager,
            message_handler=handle_kafka_message
        )

    logger.info('App lifespan: setup complete.')
    yield

    logger.info('App lifespan: tearing down async features...')

    if config.fraudio_kafka_enabled:
        await kafka_streaming.teardown()

    logger.info('App lifespan: teardown complete.')


def init_logging(config: AppConfig):
    logging_config = yaml.yaml_file_to_dict('logging.yaml')
    for logger_name in logging.root.manager.loggerDict:
        app_module = __name__.split('.')[0]
        is_app_logger = logger_name == app_module or logger_name.startswith(app_module + '.')
        configured_loggers = logging_config['loggers']
        if not is_app_logger and not logger_name in configured_loggers:
            configured_loggers[logger_name] = {'propagate': True}
    if config.running_on_gcloud:
        client = google.cloud.logging.Client()
        logging_config['handlers']['gcloud']['class'] = 'google.cloud.logging.handlers.StructuredLogHandler'
        logging_config['handlers']['gcloud']['client'] = client
        logging_config['handlers']['gcloud_app']['class'] = 'google.cloud.logging.handlers.StructuredLogHandler'
        logging_config['handlers']['gcloud_app']['client'] = client
        logging_config['root']['handlers'][0] = 'gcloud'
        logging_config['loggers'][paths.app_name()]['handlers'][0] = 'gcloud_app'
    logging.config.dictConfig(logging_config)
    logging.getHandlerByName('stdout').setLevel(config.default_log_level)
    logging.getHandlerByName('gcloud').setLevel(config.default_log_level)
    logging.getHandlerByName('stdout_app').setLevel(config.default_app_log_level)
    logging.getHandlerByName('gcloud_app').setLevel(config.default_app_log_level)
    logging.getHandlerByName('file').setLevel(config.file_log_level)


def main():
    cnx_app = create_app()
    if ConfigLoader.get_instance().hot_reload:
        reload_dirs = [paths.app()]
        # Monkey patch to fix infinite watch loop when watching log files.
        # See https://github.com/encode/uvicorn/discussions/1978
        import watchfiles
        original_watch = watchfiles.watch

        def patched_watch(*_, **kwargs):  # Ignore CWD path that uvicorn passes as args to watchfiles.watch
            return original_watch(*reload_dirs, **kwargs)

        watchfiles.watch = patched_watch
        cnx_app.run('insight_engine.app:create_app', reload_dirs=reload_dirs)
    else:
        cnx_app.run()


if __name__ == '__main__':
    main()
