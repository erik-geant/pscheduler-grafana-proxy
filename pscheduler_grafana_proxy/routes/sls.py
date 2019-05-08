import logging

from flask import Blueprint, current_app, jsonify

from pscheduler_grafana_proxy import sls
from pscheduler_grafana_proxy.routes import common

api = Blueprint("sls-routes", __name__)
logger = logging.getLogger(__name__)


@api.route("/refresh")
def refresh_sls_db():
    sls.update_cached_mps(
        current_app.config['CONFIG_PARAMS']['sls bootstrap url'],
        common.get_redis())
    return 'OK'


@api.route("/mplist")
def return_full_sls_db():
    mps = sls.load_mps(common.get_redis())
    return jsonify(list(mps))


@api.route('/mptools')
def return_mp_tools():
    tools = set()
    for mp in sls.load_mps(common.get_redis()):
        tools |= set(mp['tools'])
    return jsonify(sorted(list(tools)))


@api.route('/mpcommunities')
def return_mp_communities():
    communities = set()
    for mp in sls.load_mps(common.get_redis()):
        communities |= set(mp['communities'])
    return jsonify(sorted(list(communities)))
