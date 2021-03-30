import os


class ConfigClass(object):
    env = os.environ.get('env')

    # NEO4J_HOST = "http://10.3.7.216:5062"
    # UTILITY_SERVICE = "http://10.3.7.222:5062"

    if env == 'test':
        NEO4J_HOST = "http://10.3.7.216:5062"
        DATAOPS = "http://10.3.7.239:5063"
        CATALOGUING = "http://10.3.7.237:5064"
        PROVENANCE_SERVICE = "http://10.3.7.202:5077"
    else:
        NEO4J_HOST = "http://neo4j.utility:5062"
        PROVENANCE_SERVICE = "http://provenance.utility:5077"
        UTILITY_SERVICE = "http://common.utility:5062"
