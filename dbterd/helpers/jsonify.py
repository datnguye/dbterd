import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):  # pragma: no cover
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if type(o).__name__ == "module":
            return o.__name__
        return super().default(o)


def mask(obj: str, mask_keys: list = ["password", "secret"]):
    obj_dict = json.loads(obj)
    for key, value in obj_dict.items():
        print(key)
        if key in mask_keys or [x for x in mask_keys if key.startswith(x)]:
            obj_dict[key] = value[0:5] + "*" * 10
        # if isinstance(value, dict):
        #     obj_dict[key] = mask(json.dumps(value, cls=EnhancedJSONEncoder), mask_keys)

    return obj_dict


def to_json(obj, mask_keys=[]):
    if not obj:
        return {}
    mask_dict = obj
    # if isinstance(mask_dict, type):
    #     mask_dict = mask(json.dumps(obj.__dict__, cls=EnhancedJSONEncoder), mask_keys)
    return json.dumps(mask_dict, indent=4, cls=EnhancedJSONEncoder)
