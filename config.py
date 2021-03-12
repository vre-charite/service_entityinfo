import os


class ConfigClass(object):
    env = os.environ.get('env')

    if env == 'test':
        NEO4J_HOST = "http://10.3.7.216:5062"
        DATAOPS = "http://10.3.7.239:5063"
        CATALOGUING = "http://10.3.7.237:5064"
    else:
        NEO4J_HOST = "http://neo4j.utility:5062"
