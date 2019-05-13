import json
import jsonschema


def test_version_request(client):
    version_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "api": {
                "type": "string",
                "pattern": r'\d+\.\d+'
            },
            "module": {
                "type": "string",
                "pattern": r'\d+\.\d+'
            }
        },
        "required": ["api", "module"],
        "additionalProperties": False
    }

    rv = client.get('/version')

    assert rv.status_code == 200
    jsonschema.validate(
        json.loads(rv.data.decode("utf-8")),
        version_schema)
