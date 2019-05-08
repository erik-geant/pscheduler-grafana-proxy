import pkg_resources

from flask import Blueprint, jsonify

api = Blueprint('default-routes', __name__)

API_VERSION = '0.1'


@api.route('/version', methods=['GET', 'POST'])
def version():
    return jsonify({
        'api': API_VERSION,
        'module':
            pkg_resources.get_distribution('pscheduler_grafana_proxy').version
    })
