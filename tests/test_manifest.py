import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest
import json

class TestWorkbench(unittest.TestCase):
    log = Logger(name='test_manifest.log')
    test = SetUpTest(log)
    project_code = "entityinfo_test_manifest"
    container = ""
    manifests = []
    exported_manifest = {} 
    files = []

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        cls.container = cls.test.create_project(cls.project_code)
        cls.file_event = {
            'filename': 'entity_info_manifest_test',
            'namespace': 'vrecore',
            'project_code': cls.project_code,
        }

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS")
        try:
            cls.test.delete_project(cls.container["id"])
            [cls.test.delete_file_node(f["id"]) for f in cls.files]
            for manifest in cls.manifests:
                cls.test.delete_manifest(manifest["id"])
        except Exception as e:
            cls.log.error("Please manual delete node and entity")
            cls.log.error(e)
            raise e

    def test_01_create_manifest(self):
        data = {
            'name': 'unittest_manifest2',
            'project_code': self.project_code,
        }
        result = self.app.post(f"/v1/manifests", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.manifests.append(res["result"])
        self.assertEqual(res["result"]["name"], "unittest_manifest2")

    def test_02_get_manifest(self):
        manifest_id = self.manifests[0]["id"]
        result = self.app.get(f"/v1/manifest/{manifest_id}")
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"]["name"], "unittest_manifest2")

    def test_03_update_manifest(self):
        manifest_id = self.manifests[0]["id"]
        payload = {
            "name": "unittest_manifest3",
        }
        result = self.app.put(f"/v1/manifest/{manifest_id}", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"]["name"], "unittest_manifest3")
        self.manifests[0]["name"] = "unittest_manifest3"

    def test_04_import_export_manifest(self):
        manifest_id = self.manifests[0]["id"]
        # Export 
        payload = {
            "manifest_id": manifest_id,
        }
        result = self.app.get(f"/v1/manifest/file/export", params=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["name"], self.manifests[0]["name"])

        # Import
        res["name"] = "unittest_manifest4"
        result = self.app.post(f"/v1/manifest/file/import", json=res)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"], "Success")

        # Get imported manifest
        payload = {
            "project_code": self.container["code"],
        }
        result = self.app.get(f"/v1/manifests", params=payload)
        res = result.json()["result"]
        for i in res:
            if i["name"] != "unittest_manifest3":
                self.assertEqual(i["name"], "unittest_manifest4")
                self.manifests.append(i)
                break

    def test_05_delete_manifest(self):
        manifest_id = self.manifests.pop()["id"]
        result = self.app.delete(f"/v1/manifest/{manifest_id}")
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"], "success")

    def test_06_manifest_query(self):
        extra_data = {
            "manifest_id": self.manifests[0]["id"],
        }
        file = self.test.create_file(self.file_event, extra_data=extra_data)
        self.files.append(file)
        payload = {
            "geid_list": [file["global_entity_id"]],
        }
        result = self.app.post(f"/v1/manifest/query", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(len(res["result"]), 1)

    def test_07_manifest_list_missing_project_code(self):
        result = self.app.get(f"/v1/manifests")
        self.log.info(result)
        res = result.json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(res["detail"][0]["msg"], "field required")

    def test_08_create_manifest(self):
        data = {
            'name': 'unittest_manifest3',
            'project_code': self.project_code,
        }
        result = self.app.post(f"/v1/manifests", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["result"], "duplicate manifest name")

    def test_09_get_manifset_404(self):
        bad_id = 999999
        result = self.app.get(f"/v1/manifest/{bad_id}")
        self.log.info(result)
        self.assertEqual(result.status_code, 404)
        res = result.json()
        self.assertEqual(res["error_msg"], "Manifest not found")

    def test_10_update_manifest_404(self):
        bad_id = 999999
        payload = {
            "name": "unittest_manifest3",
        }
        result = self.app.put(f"/v1/manifest/{bad_id}", json=payload)
        self.log.info(result)
        self.assertEqual(result.status_code, 404)
        res = result.json()
        self.assertEqual(res["error_msg"], "Manifest not found")

    def test_11_delete_manifest_404(self):
        bad_id = 999999
        result = self.app.delete(f"/v1/manifest/{bad_id}")
        self.log.info(result)
        self.assertEqual(result.status_code, 404)
        res = result.json()
        self.assertEqual(res["error_msg"], "Manifest not found")

    def test_12_import_manifest_attributes(self):
        with open("tests/import_test.json", 'r') as f:
            payload = json.loads(f.read())
        payload["name"] = "unittest_manifest5"
        payload["project_code"] = self.container["code"]
        result = self.app.post(f"/v1/manifest/file/import", json=payload)
        self.log.info(result)
        print(result.json())
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.assertEqual(res["result"], "Success")

        # Get imported manifest
        payload = {
            "project_code": self.container["code"],
        }
        result = self.app.get(f"/v1/manifests", params=payload)
        res = result.json()["result"]
        for i in res:
            if i["name"] == "unittest_manifest5":
                self.manifests.append(i)
                break

    def test_13_import_dup(self):
        with open("tests/import_test.json", 'r') as f:
            payload = json.loads(f.read())
        payload["name"] = "unittest_manifest5"
        payload["project_code"] = self.container["code"]
        result = self.app.post(f"/v1/manifest/file/import", json=payload)
        self.log.info(result)
        print(result.json())
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["result"], "duplicate manifest name")

        # Get imported manifest
        payload = {
            "project_code": self.container["code"],
        }
        result = self.app.get(f"/v1/manifests", params=payload)
        res = result.json()["result"]
        for i in res:
            if i["name"] == "unittest_manifest5":
                self.manifests.append(i)
                break

    def test_14_import_dup(self):
        with open("tests/import_test.json", 'r') as f:
            payload = json.loads(f.read())
        payload["name"] = "unittest_manifest6"
        payload["project_code"] = self.container["code"]
        payload["attributes"].append({"name": "attr1"})
        result = self.app.post(f"/v1/manifest/file/import", json=payload)
        self.log.info(result)
        print(result.json())
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["result"], "duplicate attribute")

        # Get imported manifest
        payload = {
            "project_code": self.container["code"],
        }
        result = self.app.get(f"/v1/manifests", params=payload)
        res = result.json()["result"]
        for i in res:
            if i["name"] == "unittest_manifest6":
                self.manifests.append(i)
                break
