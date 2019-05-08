"""
testing startup
"""

if __name__ == "__main__":
    import logging
    import sys
    import pscheduler_grafana_proxy

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG)

    app = pscheduler_grafana_proxy.create_app()
    app.run(host="0.0.0.0", port="9876")
