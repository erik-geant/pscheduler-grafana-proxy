import logging
import time

from flask import Blueprint, current_app, jsonify, Response

from pscheduler_grafana_proxy import sls
from pscheduler_grafana_proxy.routes import common

api = Blueprint("sls-routes", __name__)


@api.route("/refresh")
def refresh_sls_db():
    sls.update_cached_mps(
        current_app.config['CONFIG_PARAMS']['sls bootstrap url'],
        common.get_redis())
    return 'OK'


@api.route("/mplist/<string:tool>")
def return_full_sls_db(tool):
    mps = sls.load_mps(tool, common.get_redis())
    return jsonify(list(mps))
