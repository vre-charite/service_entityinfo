import requests
import time
from config import ConfigClass
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db
from app import app
from resources.helpers import get_geid


class SetupException(Exception):
    "Failed setup test"


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
        testing_api = ConfigClass.NEO4J_SERVICE + "nodes/Dataset"
        params = {"name": "EntityInfoUnitTest",
                  "path": code,
                  "code": code,
                  "description": "Project created by unit test, will be deleted soon...",
                  "discoverable": discoverable,
                  "type": "Usecase",
                  "tags": ['test'],
                  "global_entity_id": get_geid() 
                  }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {params}")
        try:
            res = requests.post(testing_api, json=params)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            node = res.json()[0]
            return node
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e

    def delete_project(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete project".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/node/%s" % str(node_id)
        try:
            self.log.info(f"DELETE Project: {node_id}")
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
        project_id = file_event.get('project_id')
        if namespace == 'vrecore':
            path = f"/vre-data/{project_code}"
        else:
            path = f"/data/vre-storage/{project_code}/{file_type}"
        geid_res = requests.get(ConfigClass.UTILITY_SERVICE + "utility/id")
        self.log.info(f"Getting global entity ID: {geid_res.text}")
        global_entity_id = geid_res.json()['result']
        if namespace.lower() == 'vrecore':
            namespace_label = 'VRECore'
        else:
            namespace_label = 'Greenroom'
        payload = {
                      "file_size": 1000,
                      "full_path": path + '/' + filename,
                      "path": path,
                      "generate_id": "undefined",
                      "guid": "unittest_guid",
                      "namespace": namespace,
                      "uploader": "unittest",
                      "project_id": project_id,
                      "name": filename,
                      "input_file_id": global_entity_id,
                      "process_pipeline": "raw",
                      "operator": "entity_info_unittest",
                      "tags": ['tag1', 'tag2'],
                      "global_entity_id": global_entity_id,
                      "parent_folder_geid": "None",
                      "project_code": project_code,
                      "extra_labels": [namespace_label]
                    }
        testing_api = ConfigClass.NEO4J_SERVICE + "nodes/File"
        self.log.info(f"File created in {path}")
        try:
            self.log.info(f'POST API: {testing_api}')
            self.log.info(f'POST payload: {payload}')
            res = requests.post(testing_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            result = res.json()[0]
            file_id = result.get('id')
            relation_payload = {"start_id": project_id,
                                "end_id": file_id}
            relation_api = ConfigClass.NEO4J_SERVICE + "relations/own"
            relation_res = requests.post(relation_api, json=relation_payload)
            self.log.info(f"Create relation res: {relation_res.text}")

            # get folder id by geid
            if file_event.get("parent_geid"):
                folder_query = {"global_entity_id": file_event.get("parent_geid")}
                response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/Folder/query", json=folder_query)
                folder_node = response.json()[0]
                relation_payload = {"start_id": folder_node["id"], "end_id": file_id}
                relation_api = ConfigClass.NEO4J_SERVICE + "relations/own"
                relation_res = requests.post(relation_api, json=relation_payload)
                self.log.info(f"Create relation res: {relation_res.text}")
            return result
        except Exception as e:
            self.log.info(f"ERROR CREATING FILE: {e}")
            raise e

    def create_folder(self, geid, project_code):
        self.log.info("\n")
        self.log.info("Creating testing folder".ljust(80, '-'))
        payload = {
            "global_entity_id": geid,
            "folder_name": "entityinfo_unittest_folder",
            "folder_level": 0,
            "uploader": "EntityInfoUnittest",
            "folder_relative_path": "",
            "zone": "greenroom",
            "project_code": project_code,
            "folder_tags": [],
            "folder_parent_geid": "",
            "folder_parent_name": "",
        }
        testing_api = '/v1/folders'
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            result = res.json().get('result')
            return result
        except Exception as e:
            self.log.info(f"ERROR CREATING FOLDER: {e}")
            raise e

    def delete_folder_node(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete folder node".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "nodes/Folder/node/%s" % str(node_id)
        try:
            delete_res = requests.delete(delete_api)
            self.log.info(f"DELETE STATUS: {delete_res.status_code}")
            self.log.info(f"DELETE RESPONSE: {delete_res.text}")
        except Exception as e:
            self.log.info(f"ERROR DELETING FILE: {e}")
            self.log.info(f"PLEASE DELETE THE FILE MANUALLY WITH ID: {node_id}")
            raise e

    def delete_file_node(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete file node".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "nodes/File/node/%s" % str(node_id)
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

    def delete_workbench_records(self, project_geid):
        response = self.app.get(f"/v1/{project_geid}/workbench")
        if response.status_code != 200:
            self.log.info("ERROR DELETING WORKBENCH SQL ENTRY")
        for key, value in response.json().get("result").items():
            id = value["id"]
            response = self.app.delete(f"/v1/{project_geid}/workbench/{id}")
        return

