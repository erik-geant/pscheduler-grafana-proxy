import logging
import time
import jsonschema

from flask import Blueprint, current_app, request

from pscheduler_grafana_proxy import sls
from pscheduler_grafana_proxy.routes import common

api = Blueprint("measurement-routes", __name__)

EXPECTED_TEST_PARAMS_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'type': 'object',
    'properties': {
        'schema': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 1
        },
        'schedule': {
            'type': 'object',
            'properties': {
                'repeat': {'type': 'string'},
                'until': {'type': 'string'},
                'slip': {'type': 'string'}
            },
            'required': ['repeat', 'until', 'slip'],
            'additionalProperties': False
        },
        'test': {
            'type': 'object',
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['throughput', 'latency']
                },
                'spec': {
                    'type': 'object',
                    'properties': {
                        'schema': {
                            'type': 'integer',
                            'minimum': 1,
                            'maximum': 1
                        },
                        'source': {'type': 'string'},
                        'dest': {'type': 'string'},
                        'output-raw': {'type': 'boolean'},
                        'packet-count': {'type': 'integer'},
                        'interval': {'type': 'string'},
                        'duration': {'type': 'string'}
                    },
                    'required': ['schema', 'source', 'dest'],
                    'additionalProperties': True
                },
            },
            'required': ['type', 'spec'],
            'additionalProperties': False
        }
    },
    'required': ['schema', 'schedule', 'test'],
    'additionalProperties': False
}


@api.route('/run', methods=['POST'])
def run_measurement():
    request_payload = request.get_json()
    jsonschema.validate(request_payload, EXPECTED_TEST_PARAMS_SCHEMA)
    return 'OK'
