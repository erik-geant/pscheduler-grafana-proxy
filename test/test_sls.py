import json
import logging
import responses
import jsonschema
import pytest
from pscheduler_grafana_proxy import sls

logging.basicConfig(level=logging.INFO)

MP_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "name": {"type": "string"},
            "domains": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["hostname", "name", "communities"]
    }
}

LIST_OF_STRINGS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "minItems": 1,
    "items": {"type": "string"}
}


@responses.activate
def test_sls_mps(mocked_sls, mocked_redis):
    sls.update_cached_mps(mocked_sls, mocked_redis)
    mps = sls.load_mps(mocked_redis)
    jsonschema.validate(list(mps), MP_RESPONSE_SCHEMA)



test_data = [
    [
        "http://200.143.240.132/esmond/perfsonar/archive",
        "200.143.240.132"
    ],
    [
        "https://200.143.240.132/esmond/perfsonar/archive",
        "200.143.240.132"
    ],
    [
        "tcp://mp-pop-sj-remep.perf.pop-sc.rnp.br:861",
        "mp-pop-sj-remep.perf.pop-sc.rnp.br"
    ],
    [
        "periboea.kenyon.edu",
        "periboea.kenyon.edu"
    ],
    [
        "http://periboea.kenyon.edu/esmond/perfsonar/archive",
        "periboea.kenyon.edu"
    ],
    [
        "https://periboea.kenyon.edu/esmond/perfsonar/archive",
        "periboea.kenyon.edu"
    ],
    [
        "tcp://[2804:1454:1002:100::27]:4823",
        "[2804:1454:1002:100::27]"
    ],
    [
        "tcp://191.36.79.27:4823",
        "191.36.79.27"
    ],
    [
        "200.143.233.6",
        "200.143.233.6"
    ],
    [
        "tcp://sampaps02.if.usp.br:861",
        "sampaps02.if.usp.br"
    ],
    [
        "tcp://[2001:12d0:8120::136]:861",
        "[2001:12d0:8120::136]"
    ],
    [
        "http://200.17.30.136/services/MP/BWCTL",
        "200.17.30.136"
    ],
    [
        "http://[2001:12d0:8120::136]/services/MP/BWCTL",
        "[2001:12d0:8120::136]"
    ],
    [
        "https://200.17.30.136/services/MP/BWCTL",
        "200.17.30.136"
    ],
    [
        "https://[2001:12d0:8120::136]/services/MP/BWCTL",
        "[2001:12d0:8120::136]"
    ],
    [
        "http://[2804:1f10:8000:801::141]/esmond/perfsonar/archive",
        "[2804:1f10:8000:801::141]"
    ],
    [
        "http://152.84.101.141/esmond/perfsonar/archive",
        "152.84.101.141"
    ],
    [
        "https://[2804:1f10:8000:801::141]/esmond/perfsonar/archive",
        "[2804:1f10:8000:801::141]"
    ],
    [
        "https://152.84.101.141/esmond/perfsonar/archive",
        "152.84.101.141"
    ],
    [
        "http://[2a00:139c:5:4102::6]/esmond/perfsonar/archive",
        "[2a00:139c:5:4102::6]"
    ],
    [
        "https://[2a00:139c:5:4102::6]/esmond/perfsonar/archive",
        "[2a00:139c:5:4102::6]"
    ],
    [
        "https://[2a00:139c:5:4102::6]/pscheduler",
        "[2a00:139c:5:4102::6]"
    ],
    [
        "https://[2404:138:143:56::2]:7123",
        "[2404:138:143:56::2]"
    ],
    [
        "https://[2404:138:143:52::2]/pscheduler",
        "[2404:138:143:52::2]"
    ],
    [
        "tcp://[2001:254:8004:2::2]:861",
        "[2001:254:8004:2::2]"
    ],
]


@pytest.mark.parametrize("url,expected_hostname", test_data)
def test_hostname_from_url(url, expected_hostname):
    assert sls.hostname_from_url(url) == expected_hostname


@responses.activate
def test_mplist(client):
    rv = client.get('/sls/refresh')
    assert rv.status_code == 200

    rv = client.get('/sls/mplist')
    assert rv.status_code == 200

    jsonschema.validate(json.loads(rv.data.decode("utf-8")), MP_RESPONSE_SCHEMA)


@responses.activate
def test_mptools(client):
    rv = client.get('/sls/refresh')
    assert rv.status_code == 200

    rv = client.get('/sls/mptools')
    assert rv.status_code == 200

    rsp = json.loads(rv.data.decode("utf-8"))
    jsonschema.validate(rsp, LIST_OF_STRINGS_SCHEMA)
    assert len(set(rsp)) == len(rsp), 'response contains duplicates'

    for a, b in zip(rsp, sorted(rsp)):
        assert a == b, 'expected response to be sorted'


@responses.activate
def test_mpcommunities(client):
    rv = client.get('/sls/refresh')
    assert rv.status_code == 200

    rv = client.get('/sls/mpcommunities')
    assert rv.status_code == 200

    rsp = json.loads(rv.data.decode("utf-8"))
    jsonschema.validate(rsp, LIST_OF_STRINGS_SCHEMA)
    assert len(set(rsp)) == len(rsp), 'response contains duplicates'

    for a, b in zip(rsp, sorted(rsp)):
        assert a == b, 'expected response to be sorted'
