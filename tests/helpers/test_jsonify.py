import dataclasses
import json
from dbterd.helpers import jsonify


class Dummy:
    def __init__(self, str, secret_str) -> None:
        self.json_str = str
        self.secret_json_str = secret_str


@dataclasses.dataclass
class DummyData:
    json_str: str
    secret: str


class TestFile:
    def test_mask(self):
        json_str = '{"data":"dummy"}'
        assert jsonify.mask(obj=json_str) == dict({"data": "dummy"})

    def test_mask_has_masked(self):
        json_str = '{"password":"this is a secret password"}'
        assert jsonify.mask(obj=json_str) == dict({"password": "this " + "*" * 10})

    def test_mask_with_class(self):
        obj = Dummy(str="dummy", secret_str="this is a secret")
        assert jsonify.mask(
            json.dumps(obj.__dict__, cls=jsonify.EnhancedJSONEncoder)
        ) == dict({"json_str": "dummy", "secret_json_str": "this " + "*" * 10})

    def test_to_json_none(self):
        assert jsonify.to_json(obj=None) == {}

    def test_to_json(self):
        dummy = dict({"data": "dummy"})
        assert jsonify.to_json(obj=dummy) == json.dumps(
            dummy,
            indent=4,
            cls=jsonify.EnhancedJSONEncoder,
        )
