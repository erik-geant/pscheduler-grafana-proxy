import json

import responses
import pytest


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
