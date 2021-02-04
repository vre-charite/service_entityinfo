import os

class ConfigClass(object):
    env = os.environ.get('env')

    NEO4J_HOST = "http://neo4j.utility:5062"
