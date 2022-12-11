import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if type(o).__name__ == "module":
            return o.__name__
        return super().default(o)


def __mask(obj: str, masks: list = []):
    obj_dict = json.loads(obj)
    for key, value in obj_dict.items():
        if key in masks:
            obj_dict[key] = value[0:5] + "***********"
        if isinstance(value, dict):
            obj_dict[key] = __mask(json.dumps(value, cls=EnhancedJSONEncoder), masks)

    return obj_dict


def to_json(obj, masks=[]):
    if not obj:
        return {}
    mask_dict = obj
    if "__dict__" in mask_dict:
        mask_dict = __mask(json.dumps(obj.__dict__, cls=EnhancedJSONEncoder), masks)
    return json.dumps(mask_dict, indent=4, cls=EnhancedJSONEncoder)
