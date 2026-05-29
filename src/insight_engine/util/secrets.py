import pathlib
from abc import abstractmethod
from os import path

from insight_engine.config import ConfigLoader

config = ConfigLoader.get_instance()


class AbstractSecretManager:

    @abstractmethod
    def kafka_ca_cert_path(self) -> str:
        raise NotImplemented

    @abstractmethod
    def kafka_api_cert_path(self) -> str:
        raise NotImplemented

    @abstractmethod
    def kafka_api_key_path(self) -> str:
        raise NotImplemented


class CertFileSecretsManager(AbstractSecretManager):

    def __init__(self, raw_path: str):
        path_str = pathlib.Path(path.expanduser(raw_path))
        if path_str.exists():
            self.__kafka_secrets_base_path = path_str
        else:
            raise Exception(f'Could not load Kafka secrets from non-existend path "{path_str}"!')

    def path_from_secrets(self, filename: str):
        return str(self.__kafka_secrets_base_path.joinpath(filename))

    def read_from_secrets(self, filename: str):
        with open(str(self.__kafka_secrets_base_path.joinpath(filename)), 'r') as file:
            contents = file.read()
        return contents

    def kafka_ca_cert_path(self) -> str:
        return self.path_from_secrets('ca.pem')

    def kafka_api_cert_path(self) -> str:
        return self.path_from_secrets('service.cert')

    def kafka_api_key_path(self) -> str:
        return self.path_from_secrets('service.key')


def build_secrets_manager() -> AbstractSecretManager:
    return CertFileSecretsManager(config.fraudio_kafka_secrets_path)
