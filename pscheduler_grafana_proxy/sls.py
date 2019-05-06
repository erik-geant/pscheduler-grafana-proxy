import json
import logging
import re
import requests
from requests_futures.sessions import FuturesSession


def load_sls_hosts(bootstrap_url):
    rsp = requests.get(
        bootstrap_url,
        headers={"Accept": "application/json"})
    assert rsp.status_code == 200

    return [
        h["locator"] for h in rsp.json()["hosts"]
        if h["status"] == "alive"
    ]


def load_services(bootstrap_url):

    session = FuturesSession(max_workers=10)

    jobs = {url: session.get(
                url,
                headers={"Accept": "application/json"},
                params={"type": "service"})
            for url in load_sls_hosts(bootstrap_url)}

    all_responses = {}
    for url, job in jobs.items():

        try:
            rsp = job.result()
        except requests.ConnectionError as e:
            logging.error(str(e))
            continue

        if rsp.status_code == 200:
            all_responses[url] = rsp.json()
        else:
            logging.error(
                "'%s' returned status code %d" % (url, rsp.status_code))
            all_responses[url] = []
    return all_responses


# def hostname_from_url(url):
#     m = re.match("http.://(\[.*\]).*", url)
#     if m is not None:
#         return m.group(1)
#     m = re.match(".*//([^:/]+).*", url)
#     if m is not None:
#         return m.group(1)
#     return "???"


def update_cached_mps(bootstrap_url, r):
    r.set('pscheduler:sls', json.dumps(load_services(bootstrap_url)))

def fetch_sls_cache(r):
    return json.loads(r.get('pscheduler:sls').decode('utf-8'))


def hostname_from_url(url):
    m = re.match(r'^(?P<scheme>http|https|tcp)://(?P<hostname>[^/]+).*', url)
    if m is None:
        return url
    m1 = re.match(r'^(.*):[^\[\]:]+$', m.group("hostname"))
    if m1:
        return m1.group(1)
    return m.group("hostname")


def load_mps(tool, r):

    _tool_name_equivalencies = {
        "owping": {"owping", "owamp"},
        "owamp": {"owping", "owamp"},
    }

    def _has_tool(tool_name, service):
        eqtools = _tool_name_equivalencies.get(tool_name, {tool_name})
        service_type = service.get("service-type", [])
        if "pscheduler" in service_type:
            pscheduler_tools = service.get("pscheduler-tools", [])
            if eqtools & set(pscheduler_tools):
                return True
            return False
        if eqtools & set(service_type):
            return True
        return False

    sls_cache = fetch_sls_cache(r)
    for url in sls_cache.keys():
        for s in sls_cache[url]:
            if _has_tool(tool, s):

                service_locators = s.get("service-locator", [])
                service_names = s.get("service-name", [])
                if len(service_names) == 0:
                    service_name = "???"
                else:
                    service_name = service_names[0]
                communities = s.get("group-communities", [])
                for l in service_locators:
                    yield {
                        "name": service_name,
                        "hostname": hostname_from_url(l),
                        "communities": communities
                    }


if __name__ == "__main__":
    import redis
    SLS_BOOTSTRAP_URL = 'http://ps-west.es.net:8096/lookup/activehosts.json'
    REDIS_HOSTNAME = 'test-dashboard-storage01.geant.org'
    REDIS_PORT = 6379
    r = redis.StrictRedis(REDIS_HOSTNAME, REDIS_PORT)
    logging.basicConfig(level=logging.DEBUG)
    update_cached_mps(SLS_BOOTSTRAP_URL, r)
    mps = load_mps('owping', r)
    logging.info(list(mps))
