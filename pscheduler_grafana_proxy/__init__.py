"""
automatically invoved app factory
"""
import logging
import os
from flask import Flask
from flask_cors import CORS

from pscheduler_grafana_proxy import config


def create_app():
    """
    initializes app from the file named by
    CONFIG_JSON_FILENAME in the file named
    by the environment variable FLASK_SETTINGS_FILENAME
    :return: a new flask app instance
    """

    if "FLASK_SETTINGS_FILENAME" not in os.environ:
        assert False, \
            "environment variable 'FLASK_SETTINGS_FILENAME' must be defined"

    app = Flask(__name__)

    app.config.from_envvar("FLASK_SETTINGS_FILENAME")
    assert "CONFIG_JSON_FILENAME" in app.config, (
        "CONFIG_JSON_FILENAME not defined in %r"
        % os.environ["FLASK_SETTINGS_FILENAME"])

    assert os.path.isfile(app.config["CONFIG_JSON_FILENAME"]), (
        "config file %r not found" %
        app.config["CONFIG_JSON_FILENAME"])

    with open(app.config["CONFIG_JSON_FILENAME"]) as f:
        # test the config file can be loaded
        logging.info("loading config from: %r"
                     % app.config["CONFIG_JSON_FILENAME"])
        app.config["CONFIG_PARAMS"] = config.load(f)

    app.secret_key = "no one will ever guess this"

    CORS(app)

    from pscheduler_grafana_proxy.routes import default
    app.register_blueprint(default.api)

    from pscheduler_grafana_proxy.routes import sls
    app.register_blueprint(sls.api, url_prefix='/sls')

    from pscheduler_grafana_proxy.routes import measurements
    app.register_blueprint(measurements.api, url_prefix='/measurements')

    logging.debug(app.config)

    return app
