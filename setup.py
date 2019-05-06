from setuptools import setup, find_packages

setup(
    name="pscheduler_grafana_proxy",
    version="0.12",
    author="GEANT",
    author_email="swd@geant.org",
    description="wrapper for pscheduler i/o",
    url="https://github.com/erik-geant/pscheduler-grafana-proxy",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-cors",
        "requests",
        "requests-futures",
        "jsonschema",
        "redis"
    ]
)
