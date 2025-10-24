from <%my_service%>.util.serdes import json_to_obj


def raw(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()


def json_as_dict(filepath):
    with open(filepath, 'rb') as f:
        return json_to_obj(f.read())
