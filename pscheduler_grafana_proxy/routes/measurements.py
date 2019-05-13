from datetime import datetime
import json
import logging

from flask import Blueprint, request, jsonify
import jsonschema
import requests

from pscheduler_grafana_proxy.routes import common

api = Blueprint("measurement-routes", __name__)
logger = logging.getLogger(__name__)

OWPJAN_1970 = 0x83aa7e80
T32 = 2**32

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

MEASUREMENT_RESULTS__REQUEST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "mp": {"type": "string"},
        "task": {"type": "string"}
    },
    "required": ["mp", "task"],
    "additionalProperties": False
}



@api.route('/run', methods=['POST'])
def run_measurement():
    request_payload = request.get_json()
    jsonschema.validate(request_payload, EXPECTED_TEST_PARAMS_SCHEMA)

    mp_url = 'https://%s/pscheduler/tasks' % request_payload['mp']
    logger.debug("mp url: %r" % mp_url)
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


def load_data_points(mp, task):

    r = common.get_redis()

    def _get_url_json(url, schema=None, save_if=lambda x: True):
        logger.debug('loading url: %r' % url)
        rsp = r.get(url)
        if rsp:
            return json.loads(rsp.decode('utf-8'))

        rsp = requests.get(url, verify=False)
        if rsp.status_code != 200:
            logger.error(rsp)
            assert False

        result = rsp.json()
        if schema:
            jsonschema.validate(result, schema)
        if save_if and save_if(result):
            r.set(url, json.dumps(result))
        return result

    task_url = 'https://{mp}/pscheduler/tasks/{task}'.format(
        mp=mp, task=task)
    task_info_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "test": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "spec": {"type": "object"},
                },
                "required": ["type", "spec"],
                "additionalProperties": False
            },
            "schema": {"type": "integer", "minimum": 1, "maximum": 1},
            "tool": {"type": "string"},
            "href": {"type": "string"},
            "schedule": {
                "type": "object",
                "properties": {
                    "repeat": {"type": "string"},
                    "until": {"type": "string"},
                    "slip": {"type": "string"}
                },
                "required": ["repeat", "until", "slip"],
                "additionalProperties": False
            }
        },
        "required": ["test", "schema", "tool", "href", "schedule"],
        "additionalProperties": False
    }
    task_info = _get_url_json(task_url, task_info_schema)

    runs_url = 'https://{mp}/pscheduler/tasks/{task}/runs'.format(
        mp=mp, task=task)
    list_of_strings_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {"type": "string"}
    }

    until =  datetime.strptime(
        task_info['schedule']['until'], '%Y-%m-%dT%H:%M:%S.%fZ')
    now = datetime.utcnow()

    def _schedule_is_finished(_ignored):
        return now >= until

    def _run_is_finished(r):
        return r.get('state', '?').lower() == 'finished'


    for run_url in _get_url_json(
            runs_url, list_of_strings_schema, save_if=_schedule_is_finished):

        run = _get_url_json(run_url, save_if=_run_is_finished)
        if not _run_is_finished(run):
            continue

        if task_info['test']['type'] == 'latency':
            for p in run['result']['raw-packets']:
                delta = abs(p['dst-ts'] - p['src-ts'])/T32
                ts = p['src-ts']/T32 - OWPJAN_1970
                yield delta, ts
        elif task_info['test']['type'] == 'throughput':
            start_time = datetime.strptime(
                run['start-time'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
            intervals = run['result-merged']['intervals']
            for s in [i['summary'] for i in intervals]:
                mid_ts = (s['start'] + s['end'])/2
                ts = start_time + mid_ts
                bytes = s['throughput-bytes']
                yield bytes, ts


@common.require_accepts_json
@api.route('/timeseries', methods=['POST'])
def get_measurement_timeseries():
    request_payload = request.get_json()
    jsonschema.validate(request_payload, MEASUREMENT_RESULTS__REQUEST_SCHEMA)
    data = load_data_points(request_payload['mp'], request_payload['task'])
    return jsonify(list(data))


