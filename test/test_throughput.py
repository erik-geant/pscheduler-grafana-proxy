import logging
import os
import responses
from jsonschema import validate
from perfsonar_data_helper import throughput

logging.basicConfig(level=logging.DEBUG)

THROUGHPUT_RESPONSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "start": {"type": "number", "minimum": 0.0},
            "end": {"type": "number", "minimum": 0.0},
            "bytes": {"type": "integer", "minimum": 0},
        },
        "required": ["start", "end", "bytes"]
    }
}

SOURCE = "psmall-b-3.basnet.by"
DESTINATION = "psmall-b-2.basnet.by"

RESPONSE_DATA = [
    {
        "url": "https://psmall-b-3.basnet.by/pscheduler/tasks",
        "method": responses.POST,
        "data_filenames": ["task-init-response.txt"]
    },
    {
        "url": "https://psmall-b-3.basnet.by/pscheduler/tasks/6e109b71-b6f2-4721-adef-9c47aeca2e30/runs/first",
        "method": responses.GET,
        "data_filenames": [
            "task-0.json",
            "task-1.json",
            "task-2.json",
            "task-3.json",
            "task-4.json",
            "task-5.json",
            "task-6.json",
            "task-7.json",
            "task-8.json"
        ]
    }
]


def mock_throughput_responses():

    data_path = os.path.join(os.path.dirname(__file__), "throughput")
    for rsp in RESPONSE_DATA:

        for fn in rsp["data_filenames"]:
            with open(os.path.join(data_path, fn)) as f:
                body = f.read()

            responses.add(
                rsp["method"],
                rsp["url"],
                body=body,
                match_querystring=False)


@responses.activate
def test_latency_delays():
    mock_throughput_responses()
    data = throughput.get_throughput(SOURCE, DESTINATION, polling_interval=-1)
    logging.debug(data)
    validate(data, THROUGHPUT_RESPONSE_SCHEMA)
