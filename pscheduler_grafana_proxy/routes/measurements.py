import logging

from flask import Blueprint, request
import jsonschema
import requests

api = Blueprint("measurement-routes", __name__)
logger = logging.getLogger(__name__)

EXPECTED_TEST_PARAMS_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-07/schema#',

    "definitions": {
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
        'test-spec': {
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
        'test-def': {
            'type': 'object',
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['throughput', 'latency']
                },
                'spec': {'$ref': '#/definitions/test-spec'},
            },
            'required': ['type', 'spec'],
            'additionalProperties': False
        },
        'test-params': {
            'type': 'object',
            'properties': {
                'schema': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 1
                },
                'schedule': {'$ref': '#/definitions/schedule'},
                'test': {'$ref': '#/definitions/test-def'}
            },
            'required': ['schema', 'schedule', 'test'],
            'additionalProperties': False
        }
    },

    'type': 'object',
    'properties': {
        'mp': {'type': 'string'},
        'params': {'$ref': '#/definitions/test-params'}
    },
    'required': ['mp', 'params'],
    'additionalProperties': False
}


@api.route('/run', methods=['POST'])
def run_measurement():
    request_payload = request.get_json()
    jsonschema.validate(request_payload, EXPECTED_TEST_PARAMS_SCHEMA)

    mp_url = 'https://%s/pscheduler/tasks' % request_payload['mp']
    logger.debug("mp url: '%s'" % mp_url)
    logger.debug("request data: %r" % request_payload['params'])
    rsp = requests.post(
        mp_url,
        verify=False,
        json=request_payload['params'])

    if rsp.status_code != 200:
        logger.error(rsp)
        assert False

    logger.debug("task created: %s" % rsp.text)
    return rsp.text.rstrip().replace('"', '')
