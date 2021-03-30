import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest


class TestProjectFileCheck(unittest.TestCase):
    log = Logger(name='test_project_api.log')
    test = SetUpTest(log)
    project_code = "unittest_entity_info_files"
    container_id = ''
    file_id = []
    file_guid = []

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        raw_file_event = {'filename': 'entity_info_test_1',
                          'namespace': 'greenroom',
                          'project_code': cls.project_code,
                          'file_type': 'raw'}
        straight_copy_file_event = raw_file_event.copy()
        straight_copy_file_event['filename'] = 'entity_info_test_2'
        straight_copy_file_event['file_type'] = 'processed/straight_copy'

        core_file_event = raw_file_event.copy()
        core_file_event['namespace'] = 'vrecore'
        core_file_event['filename'] = 'entity_info_test_3'
        try:
            cls.container_id = cls.test.create_project(cls.project_code)
            create_file_raw_result = cls.test.create_file(raw_file_event)
            create_file_core_result = cls.test.create_file(core_file_event)
            create_file_straight_copy_result = cls.test.create_file(straight_copy_file_event)
            cls.log.info(f"Project ID: {cls.container_id}")
            cls.log.info(f"File Info: {create_file_raw_result}")
            cls.log.info(f"File Info: {create_file_core_result}")
            cls.log.info(f"File Info: {create_file_straight_copy_result}")
            cls.raw_file_id = create_file_raw_result.get('id')
            cls.core_file_id = create_file_core_result.get('id')
            cls.copy_file_id = create_file_straight_copy_result.get('id')
            cls.file_id = [cls.raw_file_id, cls.core_file_id, cls.copy_file_id]

            cls.raw_file_guid = create_file_raw_result.get('guid')
            cls.core_file_guid = create_file_core_result.get('guid')
            cls.copy_file_guid = create_file_straight_copy_result.get('guid')

            folder_geid = "entity_info_test_geid"
            cls.folder = cls.test.create_folder(folder_geid, cls.project_code)
            raw_file_event['filename'] = "entity_info_folder_file_1"
            raw_file_event['parent_geid'] = folder_geid
            folder_file = cls.test.create_file(raw_file_event)

            cls.file_guid = [cls.raw_file_guid, cls.core_file_guid, cls.copy_file_guid, folder_file]
        except Exception as e:
            cls.log.error(f"Failed set up test due to error: {e}")
            raise unittest.SkipTest(f"Failed setup test {e}")

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS")
        cls.log.info(f"File ID: {cls.file_id}")
        cls.log.info(f"File GUID: {cls.file_guid}")
        try:
            [cls.test.delete_file_node(f) for f in cls.file_id]
            [cls.test.delete_file_entity(f) for f in cls.file_guid]
            cls.test.delete_project(cls.container_id)
            cls.test.delete_folder_node(cls.folder["id"])
        except Exception as e:
            cls.log.error("Please manual delete node and entity")
            cls.log.error(e)
            raise e

    def test_01_get_files(self):
        self.log.info("\n")
        self.log.info("01 test get_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                },
                'Folder': {
                },
            }
        }
        try:
            result = self.app.post(f"/v2/files/{self.container_id}/query", json=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.assertEqual(isinstance(res, list), True)
            file = res[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files")
            self.assertEqual(file["name"], "entityinfo_unittest_folder")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_02_get_files_pagination(self):
        self.log.info("\n")
        self.log.info("02 test get_files".center(80, '-'))
        data = {
            'page': 1, 
            'page_size': 1, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                },
                'Folder': {
                },
            }
        }
        try:
            result = self.app.post(f"/v2/files/{self.container_id}/query", json=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.assertEqual(isinstance(res, list), True)
            file = res[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files")
            self.assertEqual(file["name"], "entity_info_test_3")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_03_get_files_query(self):
        self.log.info("\n")
        self.log.info("03 test get_files_query".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                    "name": "entity_info_test_1",
                },
                'Folder': {
                    "name": "entity_info_test_1",
                },
            }
        }
        try:
            result = self.app.post(f"/v2/files/{self.container_id}/query", json=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            self.assertEqual(res["total"], 1)
            res = res.get('result')
            self.assertEqual(isinstance(res, list), True)
            file = res[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files")
            self.assertEqual(file["name"], "entity_info_test_1")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_04_get_files_order_type(self):
        self.log.info("\n")
        self.log.info("04 test get_files_order_type".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc2', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                    "name": "entity_info_test_1",
                },
                'Folder': {
                },
            }
        }
        result = self.app.post(f"/v2/files/{self.container_id}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.log.info(res)
        self.assertEqual(res["error_msg"], "Invalid order_type")

    def test_05_get_files_missing_label(self):
        self.log.info("\n")
        self.log.info("05 test get_files_missing_label".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'File': {
                    "name": "entity_info_test_1",
                },
                'Folder': {
                },
            }
        }
        result = self.app.post(f"/v2/files/{self.container_id}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.log.info(res)
        self.assertEqual(res["error_msg"], "Missing required attribute labels")

    def test_06_get_folder_files(self):
        self.log.info("\n")
        self.log.info("06 test get_folder_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                },
                'Folder': {
                },
            }
        }
        folder_geid = self.folder["global_entity_id"]
        result = self.app.post(f"/v2/files/folder/{folder_geid}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.log.info(res)
        res = res.get('result')
        self.assertEqual(isinstance(res, list), True)
        file = res[0]
        self.assertEqual(file["project_code"], "unittest_entity_info_files")
        self.assertEqual(file["name"], "entity_info_folder_file_1")

    def test_07_get_folder_files_missing_label(self):
        self.log.info("\n")
        self.log.info("07 test get_folder_files_missing_label".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': {
                'File': {
                },
                'Folder': {
                },
            }
        }
        folder_geid = self.folder["global_entity_id"]
        result = self.app.post(f"/v2/files/folder/{folder_geid}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Missing required attribute labels")

    def test_08_get_folder_files_bad_order(self):
        self.log.info("\n")
        self.log.info("08 test get_folder_files_bad_order".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc2', 
            'query': {
                'labels': ['File', 'Folder'],
                'File': {
                },
                'Folder': {
                },
            }
        }
        folder_geid = self.folder["global_entity_id"]
        result = self.app.post(f"/v2/files/folder/{folder_geid}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Invalid order_type")

    def test_09_get_folder_files_missing_query(self):
        self.log.info("\n")
        self.log.info("08 test get_folder_files_bad_order".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
        }
        folder_geid = self.folder["global_entity_id"]
        result = self.app.post(f"/v2/files/folder/{folder_geid}/query", json=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Missing required attribute query")
