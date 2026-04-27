import os
from dataclasses import dataclass
from threading import RLock
from typing import Any, Type, get_type_hints, get_origin, get_args

import yaml

from my_service.serialization.serializable import Serializable
from my_service.util.paths import repository_path, app_name

config_init_lock = RLock()


@dataclass
class AppConfig(Serializable):
    fraudio_env_display_name: str
    fraudio_env: str
    default_log_level: str
    default_app_log_level: str
    file_log_level: str
    hot_reload: bool
    openapi_ui: bool
    log_stacktraces_http_500: bool
    tracing_enabled: bool
    running_on_gcloud: bool
    cached_tables: list[str]
    cached_table_freshness_check_interval_seconds: int
    cached_table_refresh_interval_min_seconds: int
    cached_table_refresh_interval_max_seconds: int
    cached_hash_retention_seconds: int
    cached_hash_freshness_check_interval_seconds: int
    fraudio_kafka_enabled: bool
    fraudio_kafka_producer_timeout_in_seconds: int
    fraudio_kafka_servers: list[str]
    fraudio_kafka_schema_registry_url: str
    fraudio_kafka_schema_registry_user: str
    fraudio_kafka_schema_registry_pass: str
    fraudio_kafka_secrets_path: str
    fraudio_postgres_enabled: bool
    fraudio_postgres_host: str
    fraudio_postgres_port: str
    fraudio_postgres_database: str
    fraudio_postgres_user: str
    fraudio_postgres_password: str
    fraudio_postgres_min_connections: int
    fraudio_postgres_max_connections: int


class ConfigLoader:
    _instance = None
    _config = None

    @classmethod
    def get_instance(cls) -> AppConfig:
        # Avoid locking unless it's likely needed
        if cls._instance is None:
            with config_init_lock:
                if cls._instance is None:
                    cls._instance = cls._load_config()
        return cls._instance

    @staticmethod
    def _load_config() -> AppConfig:
        if ConfigLoader._config is None:
            fraudio_environment = (ConfigLoader._get_env('FRAUDIO_ENV') or 'DEV').upper()
            base_config = ConfigLoader._load_yaml_file('config/base.yaml')
            overlay_config = ConfigLoader._load_yaml_file(f'config/{fraudio_environment.lower()}.yaml')

            config_data = {**base_config, **overlay_config}
            type_hints = get_type_hints(AppConfig)
            config_with_env_overrides = {
                k: ConfigLoader._parse_from_env(k, type_hints.get(k, str)) or v
                for k, v in config_data.items()
            }
            config_final = {**config_with_env_overrides, 'fraudio_env': fraudio_environment}
            ConfigLoader._config = AppConfig.from_dict(config_final)

        return ConfigLoader._config

    @staticmethod
    def _load_yaml_file(file_path: str) -> dict:
        with open(repository_path.joinpath(file_path), 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def _parse_from_env(config_field_name: str, type_hint: Type[Any]) -> Any | None:
        key = f'{app_name().upper()}_{config_field_name.upper()}'
        value_str = ConfigLoader._get_env(key)
        if value_str is None:
            return None
        else:
            return ConfigLoader._cast(value_str, type_hint)

    @staticmethod
    def _get_env(variable: str) -> str:
        return os.environ.get(variable, None)

    @staticmethod
    def _cast(value_str: str, type_hint: Type[Any]) -> Any:
        return (
            value_str if type_hint == str else
            value_str.lower() in ("yes", "true", "t", "1") if type_hint == bool else
            int(value_str) if type_hint == int else
            float(value_str) if type_hint == float else
            [
                ConfigLoader._cast(v, get_args(type_hint)[0])
                for v in value_str.split(",")
            ] if get_origin(type_hint) == list else
            value_str
        )
