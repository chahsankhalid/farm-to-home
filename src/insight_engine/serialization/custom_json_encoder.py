from connexion.jsonifier import Jsonifier

from insight_engine.serialization.serializable import Serializable
from insight_engine.util.serdes import obj_to_json, json_to_obj

class CustomJsonEncoder(Jsonifier):

    def dumps(self, data, **_kwargs):
        if isinstance(data, Serializable):
            serializable_data = data.to_api_dict()
        elif type(data) is list and len(data) > 0 and isinstance(data[0], Serializable):
            serializable_data = [data_entry.to_api_dict() for data_entry in data]
        else:
            serializable_data = data
        return obj_to_json(serializable_data)

    def loads(self, data):
        return json_to_obj(data)
