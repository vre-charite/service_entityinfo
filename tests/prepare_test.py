import requests
import time
from config import ConfigClass
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app import app


class SetUpTest:

    def __init__(self, log):
        self.log = log
        self.app = self.create_test_client()

    def create_test_client(self):
        client = TestClient(app)
        return client

    def create_project(self, code, discoverable='true'):
        self.log.info("\n")
        self.log.info("Preparing testing project".ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/Dataset"
        params = {"name": "EntityInfoUnitTest",
                  "path": code,
                  "code": code,
                  "description": "Project created by unit test, will be deleted soon...",
                  "discoverable": discoverable,
                  "type": "Usecase",
                  "tags": ['test']
                  }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {params}")
        try:
            res = requests.post(testing_api, json=params)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            node_id = res.json()[0]['id']
            return node_id
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e

    def delete_project(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete project".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/Dataset/node/%s" % str(node_id)
        try:
            delete_res = requests.delete(delete_api)
            self.log.info(f"DELETE STATUS: {delete_res.status_code}")
            self.log.info(f"DELETE RESPONSE: {delete_res.text}")
        except Exception as e:
            self.log.info(f"ERROR DELETING PROJECT: {e}")
            self.log.info(f"PLEASE DELETE THE PROJECT MANUALLY WITH ID: {node_id}")
            raise e

    def create_file(self, file_event):
        self.log.info("\n")
        self.log.info("Creating testing file".ljust(80, '-'))
        filename = file_event.get('filename')
        file_type = file_event.get('file_type')
        namespace = file_event.get('namespace')
        project_code = file_event.get('project_code')
        if namespace == 'vrecore':
            path = f"/vre-data/{project_code}/{file_type}"
        else:
            path = f"/data/vre-storage/{project_code}/{file_type}"
        payload = {
                      "uploader": "EntityInfoUnittest",
                      "file_name": filename,
                      "path": path,
                      "file_size": 10,
                      "description": "string",
                      "namespace": namespace,
                      "data_type": file_type,
                      "labels": ['unittest'],
                      "project_code": project_code,
                      "generate_id": "",
                      "process_pipeline": "",
                      "operator": "EntityInfoUnittest",
                      "parent_query": {}
                    }
        testing_api = ConfigClass.DATAOPS + '/v1/filedata/'
        try:
            res = requests.post(testing_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            result = res.json().get('result')
            return result
        except Exception as e:
            self.log.info(f"ERROR CREATING FILE: {e}")
            raise e

    def delete_file_node(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete file node".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/File/node/%s" % str(node_id)
        try:
            delete_res = requests.delete(delete_api)
            self.log.info(f"DELETE STATUS: {delete_res.status_code}")
            self.log.info(f"DELETE RESPONSE: {delete_res.text}")
        except Exception as e:
            self.log.info(f"ERROR DELETING FILE: {e}")
            self.log.info(f"PLEASE DELETE THE FILE MANUALLY WITH ID: {node_id}")
            raise e

    def delete_file_entity(self, guid):
        self.log.info("\n")
        self.log.info("Preparing delete file entity".ljust(80, '-'))
        delete_api = ConfigClass.CATALOGUING + '/v1/entity/guid/' + str(guid)
        try:
            delete_res = requests.delete(delete_api)
            self.log.info(f"DELETE STATUS: {delete_res.status_code}")
            self.log.info(f"DELETE RESPONSE: {delete_res.text}")
        except Exception as e:
            self.log.info(f"ERROR DELETING FILE: {e}")
            self.log.info(f"PLEASE DELETE THE FILE MANUALLY WITH GUID: {guid}")
            raise e



