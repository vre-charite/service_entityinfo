import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest

project_code = "indoctestproject"

def setUpModule():
    _log = Logger(name='test_api_sys_tags.log')
    _test = SetUpTest(_log)


class FileAttributes(unittest.TestCase):
    log = Logger(name='test_file_attributes.log')
    test = SetUpTest(log)
    project_code = "indoctestproject"
    container = ""
    manifest = []

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        cls.container = cls.test.get_project_details(cls.project_code)
        cls.manifest = cls.test.get_data_manifests(cls.project_code)
        cls.manifest_id = cls.manifest[0]['attributes'][0]['manifest_id']
        cls.attribute_id = cls.manifest[0]['attributes'][0]['id']
        cls.attribute_name = cls.manifest[0]['attributes'][0]['name']
        # cls.manifest_id, cls.attribute_name = cls.test.get_data_manifests(cls.project_code)

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS")
        try:
            pass
            # cls.test.delete_project(cls.container["id"])
        except Exception as e:
            cls.log.error("Please manual delete node and entity")
            cls.log.error(e)
            raise e

    def test_01_files_attribute_attach(self):
        project_geid = self.container[0]["global_entity_id"]
        payload = {
            "project_role": "admin",
            "username": "admin",
            "project_code": self.project_code,
            "manifest_id": self.manifest_id,
            "global_entity_id": [project_geid],
            "attributes": {self.attribute_name: "2"},
            "inherit": True
        }

        result = self.app.post(f"/v1/files/attributes/attach", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)

    def test_02_missing_required_field(self):
        project_geid = self.container[0]["global_entity_id"]
        payload = {
            "project_role": "admin",
            "username": "admin",
            "global_entity_id": [project_geid],
            "attributes": {self.attribute_name: "2"},
            "inherit": True
        }

        result = self.app.post(f"/v1/files/attributes/attach", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 422)

    def test_03_invalid_manifest_id(self):
        project_geid = self.container[0]["global_entity_id"]
        payload = {
            "project_role": "admin",
            "username": "admin",
            "manifest_id": 1,
            "global_entity_id": [project_geid],
            "attributes": {self.attribute_name: "2"},
            "inherit": True
        }

        result = self.app.post(f"/v1/files/attributes/attach", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)

    def test_04_create_attribute(self):
        payload = {
              "attributes": [
                {
                    "manifest_id": self.manifest_id,
                    "name": "test1",
                    "type": "text",
                    "value": None,
                    "optional": True,
                    "project_code": self.project_code
                }
              ]
            }
        result = self.app.post(f"/v1/attributes", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)

    def test_04_create_attribute_missing_fields(self):
        payload = {
              "attributes": [
                {
                    "manifest_id": self.manifest_id,
                    "type": "text",
                    "value": None,
                    "optional": True,
                    "project_code": self.project_code
                }
              ]
            }
        result = self.app.post(f"/v1/attributes", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)

    def test_05_update_attribute(self):
        payload = {
            "name": "test_attr",
            "value": None,
            "optional": True,
            "project_code": self.project_code,
            "type": None
        }
        result = self.app.put(f"/v1/attribute/{self.attribute_id}", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)

    def test_06_update_attribute_invalid_type(self):
        payload = {
            "name": "test_attr",
            "value": None,
            "optional": True,
            "project_code": self.project_code,
            "type": "text"
        }
        result = self.app.put(f"/v1/attribute/{self.attribute_id}", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)

    def test_07_update_attribute_attr_not_found(self):
        payload = {
            "name": "test_attr",
            "value": None,
            "optional": True,
            "project_code": self.project_code,
            "type": None
        }
        result = self.app.put(f"/v1/attribute/1", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 404)

    def test_08_delete_attribute(self):
        result = self.app.delete(f"/v1/attribute/{self.attribute_id}")
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
