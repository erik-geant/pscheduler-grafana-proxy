import json
import jsonschema

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "type": "object",
    "properties": {
        "sls bootstrap url": {"type": "string"},
        "redis": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["hostname"],
            "additionalProperties": False
        }
    },
    "required": ["sls bootstrap url", "redis"],
    "additionalProperties": False
}


def load(f):
    """
    loads, validates and returns configuration parameters

    :param f: file-like object that produces the config file
    :return:
    """
    config = json.loads(f.read())
    jsonschema.validate(config, CONFIG_SCHEMA)
    if 'port' not in config['redis']:
        config['redis']['port'] = 6379
    return config
