import os
import pathlib

user_home: pathlib.Path = pathlib.Path('.').home().absolute()
app_path: pathlib.Path = pathlib.Path(__file__).absolute().parent.parent
src_path: pathlib.Path = app_path.parent
repository_path: pathlib.Path = src_path.parent


def repo_name() -> str:
    """
    :return: name of the repository (e.g. example-api)
    """
    return repository_path.name


def app_name() -> str:
    """
    :return: name of the application package (e.g. example_api)
    """
    return app_path.name


def app(*args) -> str:
    """
    :param args: path components to join to the default application path
    :return: an absolute path as a string
    """
    return str(app_path.joinpath(*args))


def ls(path: pathlib.Path) -> list[pathlib.Path]:
    if path.is_dir():
        return [pathlib.Path(p) for p in os.listdir(path)]
    else:
        return []


__all__ = [
    'repo_name',
    'app_name',
    'app_path',
    'user_home',
    'src_path',
    'repository_path'
]
