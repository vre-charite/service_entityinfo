import unittest
from tests.logger import Logger
from tests.prepare_test import SetUpTest


class TestProjectFileCheck(unittest.TestCase):
    log = Logger(name='test_project_api.log')
    test = SetUpTest(log)
    project_code = "unittest_entity_info"
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
            cls.file_guid = [cls.raw_file_guid, cls.core_file_guid, cls.copy_file_guid]
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
        except Exception as e:
            cls.log.error("Please manual delete node and entity")
            cls.log.error(e)
            raise e

    def test_01_get_raw_file(self):
        self.log.info("\n")
        self.log.info("01 test get_raw_file".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        data = {
            "type": "raw",
            "zone": "greenroom",
            "filename": "entity_info_test_1"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 200")
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.log.info(f"COMPARING Type: {isinstance(res, dict)} VS True")
            self.assertEqual(isinstance(res, dict), True)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_02_get_straight_copy_file(self):
        self.log.info("\n")
        self.log.info("02 test get_straight_copy_file".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        data = {
            "type": "processed/straight_copy",
            "zone": "greenroom",
            "filename": "entity_info_test_2"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 200")
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.log.info(f"COMPARING Type: {isinstance(res, dict)} VS True")
            self.assertEqual(isinstance(res, dict), True)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_03_get_vre_core_file(self):
        self.log.info("\n")
        self.log.info("03 test get_vre_core_file".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        data = {
            "type": "raw",
            "zone": "vrecore",
            "filename": "entity_info_test_3"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 200")
            self.assertEqual(result.status_code, 200)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.log.info(f"COMPARING Type: {isinstance(res, dict)} VS True")
            self.assertEqual(isinstance(res, dict), True)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_04_get_non_exist_file(self):
        self.log.info("\n")
        self.log.info("04 test non_exist_file".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        data = {
            "type": "raw",
            "zone": "vrecore",
            "filename": "entity_info_test_3333"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 404")
            self.assertEqual(result.status_code, 404)
            res = result.json()
            self.log.info(res)
            res = res.get('result')
            self.log.info(f"COMPARING: {res} VS 'File not found'")
            self.assertEqual(res, 'File not found')
        except Exception as e:
            self.log.error(e)
            raise e

    def test_05_get_file_with_wrong_type(self):
        self.log.info("\n")
        self.log.info("05 test get_file_with_wrong_type".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        wrong_type = "faketype"
        data = {
            "type": wrong_type,
            "zone": "greenroom",
            "filename": "entity_info_test_1"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 400")
            self.assertEqual(result.status_code, 400)
            res = result.json()
            self.log.info(res)
            res_error = res.get('error_msg')
            self.log.info(f"COMPARING error_msg: {res_error} VS Invalid type {wrong_type}")
            self.assertEqual(res_error, f'Invalid type {wrong_type}')
            res_result = res.get('result')
            self.log.info(f"COMPARING result: {res_result} VS {''}")
            self.assertEqual(res_result, {})
        except Exception as e:
            self.log.error(e)
            raise e

    def test_06_get_with_wrong_zone(self):
        self.log.info("\n")
        self.log.info("06 test get_file_with_wrong_zone".center(80, '-'))
        test_api = f'/v1/project/{self.project_code}/file/exist'
        wrong_zone = "fakezone"
        data = {
            "type": 'raw',
            "zone": wrong_zone,
            "filename": "entity_info_test_1"
        }
        try:
            result = self.app.get(test_api, params=data)
            self.log.info(result)
            self.log.info(f"COMPARING CODE: {result.status_code} VS 400")
            self.assertEqual(result.status_code, 400)
            res = result.json()
            self.log.info(res)
            res_error = res.get('error_msg')
            self.log.info(f"COMPARING error_msg: {res_error} VS Invalid zone")
            self.assertEqual(res_error, f'Invalid zone')
            res_result = res.get('result')
            self.log.info(f"COMPARING result: {res_result} VS {''}")
            self.assertEqual(res_result, {})
        except Exception as e:
            self.log.error(e)
            raise e

