import os
# os.environ['env'] = 'test'


class ConfigClass(object):
    env = os.environ.get('env')

    NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
    NEO4J_SERVICE_V2 = "http://neo4j.utility:5062/v2/neo4j/"
    PROVENANCE_SERVICE = "http://provenance.utility:5077/v1/"
    UTILITY_SERVICE = "http://common.utility:5062/v1/"
    NFS_ROOT_PATH = "/data/vre-storage"
    VRE_ROOT_PATH = "/vre-data"
    BFF_SERVICE = "http://bff.utility:5060/v1/"
    if env == 'test':
        NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
        NEO4J_SERVICE_V2 = "http://10.3.7.216:5062/v2/neo4j/"
        PROVENANCE_SERVICE = "http://10.3.7.202:5077/v1/"
        UTILITY_SERVICE = "http://10.3.7.222:5062/v1/"
        DATAOPS = "http://10.3.7.239:5063"
        CATALOGUING = "http://10.3.7.237:5064"

    RDS_HOST = "opsdb.utility"
    RDS_PORT = "5432"
    RDS_DBNAME = "INDOC_VRE"
    RDS_USER = "postgres"
    RDS_PWD = "postgres"
    if env == 'test':
        RDS_HOST = "10.3.7.215"
    if env == 'charite':
        RDS_USER = "indoc_vre"
        RDS_PWD = os.environ.get('RDS_PWD')
    RDS_SCHEMA_DEFAULT = "indoc_vre"

    SQLALCHEMY_DATABASE_URI = f"postgresql://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
