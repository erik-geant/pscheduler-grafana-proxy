import json
import logging

from perfsonar_data_helper.pscheduler import client


def get_raw(source, destination, polling_interval, status_handler=None):

    test_spec = {
        "source": source, 
        "dest": destination,
#        "packet-count": 10,
        "output-raw": True,
        "schema": 1
    }

    test_data = {
        "schema": 1,
        "schedule": {"slip": "PT5M"},
        "test": {
            "spec": test_spec,
            "type": "latency"
        }
    }

    task_url = client.create_task(source, test_data)
    task_result = client.get_task_result(
        task_url,
        polling_interval,
        status_handler)

    if "result" in task_result:
        return task_result["result"]["raw-packets"]
    elif "result-merged" in task_result:
        return task_result["result-merged"]["raw-packets"]
    else:
        assert False, "can't find result key in rsp" + str(task_result.keys())


def get_delays_debug(source, destination):
    import os
    filename = os.path.join(
        os.path.dirname(__file__),
        "..",
        "test",
        "owamp-deltas.json")
    with open(filename) as f:
        return json.loads(f.read())


def get_delays(source, destination, polling_interval, status_handler=None):
    exp = float(0x100000000)
    def _delta(x):
        rcv = float(x["dst-ts"])/exp
        snd = float(x["src-ts"])/exp
        return rcv-snd
    return [_delta(x) for x in
            get_raw(source, destination, polling_interval, status_handler)]


def format_result(task_result):
    if "raw-packets" not in task_result:
        raise client.PSchedulerError(
            "can't find raw-packets in rsp" + str(task_result.keys()))

    # reformat the result as a list of delays, in seconds
    exp = float(0x100000000)

    def _delta(x):
        rcv = float(x["dst-ts"])/exp
        snd = float(x["src-ts"])/exp
        return rcv-snd

    return [_delta(x) for x in task_result["raw-packets"]]


def make_test_data(source, destination):
    test_spec = {
        "source": source,
        "dest": destination,
        #        "packet-count": 10,
        "output-raw": True,
        "schema": 1
    }

    return {
        "schema": 1,
        "schedule": {"slip": "PT5M"},
        "test": {
            "spec": test_spec,
            "type": "latency"
        }
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SOURCE = "perfsonar-nas.asnet.am"
    DESTINATION = "perfsonar-probe.ripe.net"
    result = get_raw(
        source=SOURCE,
        destination=DESTINATION,
        polling_interval=5)
    logging.debug(result)
