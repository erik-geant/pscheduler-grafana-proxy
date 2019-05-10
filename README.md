# pScheduler/Grafana proxy

* [Overview](#overview)
* [System Requirements](#system-requirements)
* [Configuration](#configuration)
* [Running This Module](#running-this-module)
* [Web Service API](#web-service-api)
* [On-Demand Measurement User Interface](#on-demand-measurement-user-interface)


## Overview

This module provides an management layer for
configuring on-demand pScheduler measurements
and exposes the results in a format convenient
for use with Grafana.

The web service is communicates with clients over HTTP.

Non-trivial payloads are sent and received using
JSON-formatted strings.  Where relevant, the server
will return an
error unless the request contains
`Content-Type` or `Accept` headers
with the type `application/json`.

HTTP communication and JSON grammar details are
beyond the scope of this document.
Please refer to [RFC 2616](https://tools.ietf.org/html/rfc2616)
and www.json.org for more details.


## System Requirements

Read and Write access to a Redis server is required.
Redis installation and configuration details are outside
the scope of this document.


## Configuration

The web service expects two configuration files.

The filename of the first configuration file must
be stored in the `FLASK_SETTINGS_FILENAME` environment
variable, and the file itself must be formatted as
follows:

    ```python
    CONFIG_JSON_FILENAME="/path/filename.json"
    ```

The `CONFIG_JSON_FILENAME` above must be the filename
of a json file that must be formatted according to the
following schema:

    ```json
    {
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
    ```

The `redis.port` configuration parameter is optional, and
if not present the value 6379 will be used.


## Running This Module

This module has been tested in the following execution environments:

- As an embedded Flask application.
For example, the application could be launched as follows:

```bash
$ export FLASK_APP=app.py
$ export FLASK_SETTINGS_FILENAME=settings.cfg
$ flask run
```

- deployed to a wsgi server, such as:
  - `mod_wsgi/Apache`
  - `gunicorn` with or without reverse proxy behind `nginx` or `Apache`

Configuration details of these frameworks are
outside the scope of this document.

## Web Service API

## protocol specification

The following web service resources are provided by this module.

* `/sls/version`

  This resource returns a JSON object containing version
  information about the currently running module.

  The response will be formatted as follows:

  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "api": {
            "type": "string",
            "pattern": r'\d+\.\d+'
        },
        "module": {
            "type": "string",
            "pattern": r'\d+\.\d+'
        }
    },
    "required": ["api", "module"],
    "additionalProperties": False
  }
  ```

* `/sls/refresh`

  This resource walks the lookup servers found from the
  `sls bootstrap url` configuration parameters and builds
  a list of known measurement points.  The list is saved
  in the redis server.

  On success, the response is the string `OK`

* `/sls/mplist`

  This resource returns the full cache of information
  about known measurement points.

  The responses will be a JSON list of
  objects, and will formatted as follows:  (TODO: more detailed schema)

  ```json
  {
    "$schema": "http://json-schema.org/draft-06/schema#",
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
  ```


* `/sls/mptools`

  This resource returns a sorted list of test tool names
  that are supported on at least one measurement point


* `/sls/mpcommunities

  This resource returns a sorted list of community names
  for which there is at least one measurement point.


* `/measurements/run`

  This resource sends a request to a `pscheduler` instance
  to request scheduling of a repeated test measurement
  between a source and destination.

  The response will be the url of the `pscheduler`
  task info REST endpoint.

  The request must contain a JSON payload formatted as
  follows:


  ```json
  {
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
  ```

## On-Demand Measurement User Interface

The module serves a simple user interface for using
the above web service resources to create and send
a `pscheduler` measurement ask request.

The user interface is served from the url:

  - BASE_URI/static/run-measurement.html

