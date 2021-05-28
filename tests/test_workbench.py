import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest

class TestWorkbench(unittest.TestCase):
    log = Logger(name='test_workbench_api.log')
    test = SetUpTest(log)
    project_code = "entityinfo_test_workbench"
    container = ""

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        cls.container = cls.test.create_project(cls.project_code)

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS")
        try:
            cls.test.delete_project(cls.container["id"])
            cls.test.delete_workbench_records(cls.container["global_entity_id"])
        except Exception as e:
            cls.log.error("Please manual delete node and entity")
            cls.log.error(e)
            raise e

    def test_01_create_entry(self):
        data = {
            'workbench_resource': 'superset',
            'deployed': True,
            'deployed_by': 'admin',
        }
        project_geid = self.container["global_entity_id"]
        result = self.app.post(f"/v1/{project_geid}/workbench", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"], "success")

    def test_02_create_entry_another(self):
        data = {
            'workbench_resource': 'guacamole',
            'deployed': True,
            'deployed_by': 'admin',
        }
        project_geid = self.container["global_entity_id"]
        result = self.app.post(f"/v1/{project_geid}/workbench", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"], "success")

    def test_03_create_entry_invalid_resource(self):
        data = {
            'workbench_resource': 'greg',
            'deployed': True,
            'deployed_by': 'admin',
        }
        project_geid = self.container["global_entity_id"]
        result = self.app.post(f"/v1/{project_geid}/workbench", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Invalid workbench resource")

    def test_04_create_entry_missing_field(self):
        data = {
            'deployed': True,
            'deployed_by': 'admin',
        }
        project_geid = self.container["global_entity_id"]
        result = self.app.post(f"/v1/{project_geid}/workbench", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 422)
        res = result.json()

    def test_05_create_entry_duplicate(self):
        data = {
            'workbench_resource': 'guacamole',
            'deployed': True,
            'deployed_by': 'admin',
        }
        project_geid = self.container["global_entity_id"]
        result = self.app.post(f"/v1/{project_geid}/workbench", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 409)
        res = result.json()
        self.assertEqual(res["error_msg"], "Record already exists for this project and resource")

    def test_06_get_entries(self):
        project_geid = self.container["global_entity_id"]
        result = self.app.get(f"/v1/{project_geid}/workbench")
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"]["guacamole"]["deployed"], True)
        self.assertEqual(res["result"]["guacamole"]["deployed_by"], "admin")
        self.assertEqual(res["result"]["superset"]["deployed"], True)
        self.assertEqual(res["result"]["superset"]["deployed_by"], "admin")

