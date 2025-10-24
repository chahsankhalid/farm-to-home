import yaml

from <%my_service%>.util import paths


def yaml_to_dict(yaml_text) -> dict:
    yaml_dict = yaml.load(yaml_text, Loader=yaml.FullLoader)
    return yaml_dict


def yaml_file_to_str(*path_relative_to_app) -> str:
    with open(paths.app(*path_relative_to_app)) as f:
        yaml_text = f.read()
    return yaml_text


def yaml_file_to_dict(*path_relative_to_app) -> dict:
    return yaml_to_dict(yaml_file_to_str(*path_relative_to_app))
