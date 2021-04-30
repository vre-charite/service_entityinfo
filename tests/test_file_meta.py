import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest

class TestFileMetaCheck(unittest.TestCase):
    log = Logger(name='test_meta_api.log')
    test = SetUpTest(log)
    project_code = "unittest_entity_info_files_meta"
    container_id = ''
    file_id = []
    file_guid = []

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        raw_file_event = {'filename': 'entity_info_meta_test_1',
                          'namespace': 'greenroom',
                          'project_code': cls.project_code,
                          }
        straight_copy_file_event = raw_file_event.copy()
        straight_copy_file_event['filename'] = 'entity_info_meta_test_2'

        core_file_event = raw_file_event.copy()
        core_file_event['namespace'] = 'vrecore'
        core_file_event['filename'] = 'entity_info_meta_test_3'
        try:
            cls.container = cls.test.create_project(cls.project_code)
            cls.container_id = cls.container["id"]
            core_file_event['project_id'] = cls.container_id
            raw_file_event['project_id'] = cls.container_id
            straight_copy_file_event['project_id'] = cls.container_id
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

            folder_geid = "entity_info_meta_test_geid"
            cls.folder = cls.test.create_folder(folder_geid, cls.project_code)
            raw_file_event['filename'] = "entity_info_folder_file_meta_1"
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

    def test_01_get_files_meta(self):
        self.log.info("\n")
        self.log.info("01 test get_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': '{}',
            'source_type': 'Project',
            'zone': 'Greenroom',
        }
        try:
            geid = self.container["global_entity_id"]
            result = self.app.get(f"/v1/files/meta/{geid}", params=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            meta_list = res.get('data')
            self.assertEqual(isinstance(meta_list, list), True)
            file = meta_list[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files_meta")
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
            'query': '{}',
            'source_type': 'Project',
            'zone': 'All',
        }
        try:
            geid = self.container["global_entity_id"]
            result = self.app.get(f"/v1/files/meta/{geid}", params=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(f"Result: {res}")
            res = res.get('result')
            meta_list = res.get('data')
            self.assertEqual(isinstance(meta_list, list), True)
            file = meta_list[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files_meta")
            self.assertEqual(file["name"], "entity_info_meta_test_3")
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
            'query': '{"name": "entity_info_meta_test_1"}',
            'source_type': 'Project',
            'zone': 'All',
        }
        try:
            geid = self.container["global_entity_id"]
            result = self.app.get(f"/v1/files/meta/{geid}", params=data)
            self.log.info(result)
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            self.assertEqual(res["total"], 1)
            res = res.get('result')
            meta_list = res.get('data')
            self.assertEqual(isinstance(meta_list, list), True)
            file = meta_list[0]
            self.assertEqual(file["project_code"], "unittest_entity_info_files_meta")
            self.assertEqual(file["name"], "entity_info_meta_test_1")
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
            'query': '{"name": "entity_info_meta_test_1"}',
            'source_type': 'Project',
            'zone': 'All',
        }
        geid = self.container["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.log.info(res)
        self.assertEqual(res["error_msg"], "Invalid order_type")

    def test_05_get_files_missing_zone(self):
        self.log.info("\n")
        self.log.info("05 test get_files_missing_zone".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': '{"name": "entity_info_meta_test_1"}',
            'source_type': 'Project',
        }
        geid = self.container["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.assertEqual(result.status_code, 422)
        res = result.json()
        print(res)
        self.log.info(res)
        self.assertEqual(res["detail"][0]['msg'], "field required")

    def test_06_get_folder_files(self):
        self.log.info("\n")
        self.log.info("06 test get_folder_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'source_type': 'Folder',
            'zone': 'All',
        }
        geid = self.folder["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.log.info(res)
        res = res.get('result')
        meta_list = res.get('data')
        self.assertEqual(isinstance(meta_list, list), True)
        file = meta_list[0]
        self.assertEqual(file["project_code"], "unittest_entity_info_files_meta")
        self.assertEqual(file["name"], "entity_info_folder_file_meta_1")

    def test_07_get_folder_files_missing_source_type(self):
        self.log.info("\n")
        self.log.info("07 test get_folder_files_missing_source_type".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': '{"name": "entity_info_meta_test_1"}',
            'zone': 'All',
        }
        geid = self.folder["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 422)
        res = result.json()
        self.assertEqual(res["detail"][0]['msg'], "field required")

    def test_08_get_folder_files_bad_order(self):
        self.log.info("\n")
        self.log.info("08 test get_folder_files_bad_order".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc2', 
            'query': '{"name": "entity_info_meta_test_1"}',
            'zone': 'All',
            'source_type': 'Folder',
        }
        geid = self.folder["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
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

    def test_10_get_folder_files_bad_source_type(self):
        self.log.info("\n")
        self.log.info("07 test get_folder_files_missing_source_type".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': '{"name": "entity_info_meta_test_1"}',
            'zone': 'All',
            'source_type': 'bad',
        }
        geid = self.folder["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Invalid source_type")

    def test_11_get_folder_files_bad_zone(self):
        self.log.info("\n")
        self.log.info("07 test get_folder_files_bad_zone".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'query': '{"name": "entity_info_meta_test_1"}',
            'zone': 'bad',
            'source_type': 'Folder',
        }
        geid = self.folder["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 400)
        res = result.json()
        self.assertEqual(res["error_msg"], "Invalid zone")

    def test_12_get_folder_files_partial(self):
        self.log.info("\n")
        self.log.info("06 test get_folder_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'source_type': 'Project',
            'query': '{"name": "entity_info_meta_test"}',
            'partial': '["name"]',
            'zone': 'All',
        }
        geid = self.container["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.log.info(res)
        res = res.get('result')
        meta_list = res.get('data')
        self.assertEqual(isinstance(meta_list, list), True)
        self.assertEqual(len(meta_list), 3)

    def test_13_get_folder_files_trash(self):
        self.log.info("\n")
        self.log.info("06 test get_folder_files".center(80, '-'))
        data = {
            'page': 0, 
            'page_size': 10, 
            'order_by': 'name', 
            'order_type': 'desc', 
            'source_type': 'TrashFile',
            'zone': 'All',
        }
        geid = self.container["global_entity_id"]
        result = self.app.get(f"/v1/files/meta/{geid}", params=data)
        self.log.info(result)
        self.assertEqual(result.status_code, 200)
        res = result.json()
        self.log.info(res)
        res = res.get('result')
        meta_list = res.get('data')
        self.assertEqual(isinstance(meta_list, list), True)
        self.assertEqual(len(meta_list), 0)
