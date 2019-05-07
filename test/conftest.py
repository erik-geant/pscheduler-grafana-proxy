import json
import os
import tempfile

import pytest
import responses

import pscheduler_grafana_proxy


@pytest.fixture
def flask_config():
    with tempfile.TemporaryDirectory() as dir_name:
        app_params = {
            'sls bootstrap url': 'http://ps-west.es.net:8096/lookup/activehosts.json',
            'redis': {
                'hostname': 'test-dashboard-storage01.geant.org'
            }
        }

        app_config_filename = os.path.join(dir_name, 'config.json')
        with open(app_config_filename, 'w') as f:
            f.write(json.dumps(app_params))

        flask_config_filename = os.path.join(dir_name, 'flask.config')
        with open(flask_config_filename, 'w') as f:
            f.write('CONFIG_JSON_FILENAME = "%s"' % app_config_filename)

        yield flask_config_filename


@pytest.fixture
def client(flask_config):
    os.environ['FLASK_SETTINGS_FILENAME'] = flask_config
    return pscheduler_grafana_proxy.create_app().test_client()


def _mock_responses(response_data):

    for rsp in response_data:

        for data_filename in rsp['data_filenames']:
            with open(data_filename) as f:
                body = f.read()

            responses.add(
                rsp['method'],
                rsp['url'],
                body=body,
                match_querystring=False)


@pytest.fixture
def mocked_latency_test_data():

    data_path = os.path.join(os.path.dirname(__file__), 'latency')

    SOURCE = 'perfsonar-nas.asnet.am'
    DESTINATION = 'perfsonar-probe.ripe.net'

    RESPONSE_DATA = [
        {
            'aaa': data_path,
            'url': 'https://perfsonar-nas.asnet.am/pscheduler/tasks',
            'method': responses.POST,
            'data_filenames': [
                os.path.join(data_path, 'task-init-response.txt')]
        },
        {
            'url': 'https://perfsonar-nas.asnet.am/'
                   'pscheduler/tasks/'
                   '6f86acbf-ee3b-497d-857b-6c7975f1ac00/runs/first',
            'method': responses.GET,
            'data_filenames': [
                os.path.join(data_path, 'task-0.json'),
                os.path.join(data_path, 'task-1.json'),
                os.path.join(data_path, 'task-2.json'),
                os.path.join(data_path, 'task-3.json'),
                os.path.join(data_path, 'task-4.json'),
                os.path.join(data_path, 'task-5.json'),
                os.path.join(data_path, 'task-6.json'),
                os.path.join(data_path, 'task-7.json'),
                os.path.join(data_path, 'task-8.json'),
                os.path.join(data_path, 'task-9.json'),
                os.path.join(data_path, 'task-10.json'),
                os.path.join(data_path, 'task-11.json'),
                os.path.join(data_path, 'task-12.json'),
                os.path.join(data_path, 'task-13.json'),
                os.path.join(data_path, 'task-14.json')
            ]
        }
    ]

    _mock_responses(RESPONSE_DATA)

    return {
        'source': SOURCE,
        'destination': DESTINATION
    }


@pytest.fixture
def mocked_throughput_test_data():

    data_path = os.path.join(os.path.dirname(__file__), 'throughput')

    SOURCE = 'psmall-b-3.basnet.by'
    DESTINATION = 'psmall-b-2.basnet.by'

    RESPONSE_DATA = [
        {
            'url': 'https://psmall-b-3.basnet.by/pscheduler/tasks',
            'method': responses.POST,
            'data_filenames': [
                os.path.join(data_path, 'task-init-response.txt')]
        },
        {
            'url': 'https://psmall-b-3.basnet.by/pscheduler/tasks/'
                   '6e109b71-b6f2-4721-adef-9c47aeca2e30/runs/first',
            'method': responses.GET,
            'data_filenames': [
                os.path.join(data_path, 'task-0.json'),
                os.path.join(data_path, 'task-1.json'),
                os.path.join(data_path, 'task-2.json'),
                os.path.join(data_path, 'task-3.json'),
                os.path.join(data_path, 'task-4.json'),
                os.path.join(data_path, 'task-5.json'),
                os.path.join(data_path, 'task-6.json'),
                os.path.join(data_path, 'task-7.json'),
                os.path.join(data_path, 'task-8.json')
            ]
        }
    ]

    _mock_responses(RESPONSE_DATA)

    return {
        'source': SOURCE,
        'destination': DESTINATION
    }


@pytest.fixture
def mocked_sls_test_data():

    data_path = os.path.join(os.path.dirname(__file__), 'sls')

    BOOTSTRAP_URL = 'http://ps-west.es.net:8096/lookup/activehosts.json'

    # test data
    # data files are in the test/sls directory
    SLS_DATA = {
        BOOTSTRAP_URL: 'activehosts.json',
        'http://ps-west.es.net:8090/lookup/records':
            'ps-west.es.net.json',
        'http://ps-east.es.net:8090/lookup/records':
            'ps-east.es.net.json',
        'http://monipe-ls.rnp.br:8090/lookup/records':
            'monipe-ls.rnp.br.json',
        'http://ps-sls.sanren.ac.za:8090/lookup/records':
            'ps-sls.sanren.ac.za.json',
        'http://nsw-brwy-sls1.aarnet.net.au:8090/lookup/records':
            'nsw-brwy-sls1.aarnet.net.au.json'
    }

    RESPONSE_DATA = []
    for url, filename in SLS_DATA.items():

        RESPONSE_DATA.append({
            'url': url,
            'method': responses.GET,
            'data_filenames': [os.path.join(data_path, filename)]
        })

        RESPONSE_DATA.append({
            'url': url + '/',
            'method': responses.GET,
            'data_filenames': [os.path.join(data_path, filename)]
        })

    _mock_responses(RESPONSE_DATA)

    return {
        'bootstrap_url': BOOTSTRAP_URL
    }
