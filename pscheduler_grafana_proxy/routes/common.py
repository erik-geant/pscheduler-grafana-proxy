import functools
import logging

from flask import request, Response, current_app, g
import redis

logger = logging.getLogger(__name__)


def get_redis():
    if 'redis_db' not in g:
        config = current_app.config['CONFIG_PARAMS']
        g.redis_db = redis.StrictRedis(
            host=config['redis']['hostname'],
            port=config['redis']['port'])

    return g.redis_db


def require_accepts_json(f):
    """
    used as a route handler decorator to return an error
    unless the request allows responses with type "application/json"
    :param f: the function to be decorated
    :return: the decorated function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: use best_match to disallow */* ...?
        if not request.accept_mimetypes.accept_json:
            return Response(
                response="response will be json",
                status=406,
                mimetype="text/html")
        return f(*args, **kwargs)
    return decorated_function
