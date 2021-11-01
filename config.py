import os
import requests
from requests.models import HTTPError

srv_namespace = "service_entityinfo"
CONFIG_CENTER = "http://10.3.7.222:5062" \
    if os.environ.get('env', "test") == "test" \
    else "http://common.utility:5062"


def vault_factory() -> dict:
    url = CONFIG_CENTER + \
        "/v1/utility/config/{}".format(srv_namespace)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class ConfigClass(object):
    vault = vault_factory()
    env = os.environ.get('env')
    disk_namespace = os.environ.get('namespace')
    version = "0.1.0"
    # disk mounts
    NFS_ROOT_PATH = "/data/vre-storage"
    VRE_ROOT_PATH = "/vre-data"
    ROOT_PATH = {
        "vre": "/vre-data"
    }.get(os.environ.get('namespace'), "/data/vre-storage")

    NEO4J_SERVICE = vault['NEO4J_SERVICE']+"/v1/neo4j/"
    ENTITYINFO_SERVICE = vault['ENTITYINFO_SERVICE']+"/v1/"
    NEO4J_SERVICE_V2 = vault['NEO4J_SERVICE']+"/v2/neo4j/"
    PROVENANCE_SERVICE = vault['PROVENANCE_SERVICE']+"/v1/"
    UTILITY_SERVICE = vault['UTILITY_SERVICE']+"/v1/"
    BFF_SERVICE = vault['BFF_SERVICE']+"/v1/"
    DATAOPS = vault["DATA_OPS_UTIL"]
    CATALOGUING = vault["CATALOGUING_SERVICE"]

    RDS_HOST = vault['RDS_HOST']
    RDS_PORT = vault['RDS_PORT']
    RDS_DBNAME = vault['RDS_DBNAME']
    RDS_USER = vault['RDS_USER']
    RDS_PWD = vault['RDS_PWD']
    RDS_SCHEMA_DEFAULT = vault['RDS_SCHEMA_DEFAULT']
    SQLALCHEMY_DATABASE_URI = f"postgresql://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
