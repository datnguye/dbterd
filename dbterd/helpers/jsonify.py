import dataclasses
import json
from typing import Optional, Union


class EnhancedJSONEncoder(json.JSONEncoder):  # pragma: no cover
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if type(o).__name__ == "module":
            return o.__name__
        return super().default(o)


def mask(obj: str, mask_keys: Optional[list[str]] = None) -> dict:
    """Mask sensitive values in a JSON string.

    Args:
        obj: JSON string to mask
        mask_keys: List of keys to mask (defaults to password, secret)

    Returns:
        Dictionary with masked values
    """
    if mask_keys is None:
        mask_keys = ["password", "secret"]
    obj_dict = json.loads(obj)
    for key, value in obj_dict.items():
        print(key)
        if key in mask_keys or [x for x in mask_keys if key.startswith(x)]:
            obj_dict[key] = value[0:5] + "*" * 10

    return obj_dict


def to_json(obj: object, mask_keys: Optional[list[str]] = None) -> Union[str, dict]:
    """Convert object to JSON string.

    Args:
        obj: Object to serialize (supports dataclasses)
        mask_keys: Optional list of keys to mask

    Returns:
        JSON string representation, or empty dict if obj is falsy
    """
    if mask_keys is None:
        mask_keys = []
    if not obj:
        return {}
    mask_dict = obj
    return json.dumps(mask_dict, indent=4, cls=EnhancedJSONEncoder)
