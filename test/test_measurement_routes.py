import json
import os

import jsonschema
import pytest
import responses


@responses.activate
@pytest.mark.parametrize('measurement_params', [
    {"schema":1,"schedule":{"repeat":"PT5M","slip":"PT5M","until":"2019-05-07T20:02:13.144Z"},"test":{"type":"latency","spec":{"schema":1,"source":"nlg-perfsonar-1.northernlights.gigapop.net","dest":"infotech-sv-62.ggnet.umn.edu","output-raw":True,"packet-count":10}}},  # noqa: E501, E231
    {"schema":1,"schedule":{"repeat":"PT5M","slip":"PT5M","until":"2019-05-07T20:06:59.018Z"},"test":{"type":"throughput","spec":{"schema":1,"source":"89.188.60.70","dest":"37.26.173.34","interval":"PT5S","duration":"PT30S"}}}  # noqa: E501, E231
])
def test_latency_delays_http(client, measurement_params):

    mp_hostname = 'aaa.bbb.ccc'
    mp_url = 'https://%s/pscheduler/tasks' % mp_hostname

    responses.add('POST', mp_url, body='aabbccdd')

    request_payload = {
        'mp': mp_hostname,
        'params': measurement_params
    }

    rv = client.post(
        '/measurements/run',
        data=json.dumps(request_payload),
        content_type='application/json')

    assert rv.status_code == 200
    assert rv.data.decode('utf-8') == 'aabbccdd'


def _mock_measurement_responses(dirname):

    with open(os.path.join(dirname, 'test-data.json')) as f:
        params = json.loads(f.read())

    data = {
        'https://{mp}/pscheduler/tasks/{task}'.format(**params):
            'task-info.json',
        'https://{mp}/pscheduler/tasks/{task}/runs'.format(**params):
            'runs.json',
    }

    for run_id in params['runs']:
        url = 'https://{mp}/pscheduler/tasks/{task}/runs/{run}'.format(
            run=run_id, **params)
        data[url] = '{run}.json'.format(run=run_id)

    for url, filename in data.items():
        with open(os.path.join(dirname, filename)) as f:
            body = f.read()
        responses.add(responses.GET, url, body=body)

    return params


@pytest.mark.parametrize('test_data_dirname', [
    os.path.join(os.path.dirname(__file__), 'measurements', 'owamp'),
    os.path.join(os.path.dirname(__file__), 'measurements', 'iperf3')
])
@responses.activate
def test_latency_timeseries(client, test_data_dirname):
    params = _mock_measurement_responses(test_data_dirname)
    payload = {
        'mp': params['mp'],
        'task': params['task']
    }

    rv = client.post(
        '/measurements/timeseries',
        data=json.dumps(payload),
        content_type='application/json')

    assert rv.status_code == 200

    timeseries_schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        "type": "array",
        "items": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 2
        },
        "minItems": 1
    }
    data = json.loads(rv.data.decode('utf-8'))
    jsonschema.validate(data, timeseries_schema)
