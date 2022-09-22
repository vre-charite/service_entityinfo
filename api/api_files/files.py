# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import math
import os
import time
import copy

import httpx
from fastapi import APIRouter
from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

from api.api_files.utils import check_attributes
from api.api_files.utils import get_file_node_bygeid
from api.api_files.utils import has_valid_attributes
from api.api_files.utils import get_container_id
from config import ConfigClass
from models import files as models
from models import folders as folder_models
from models import manifest
from models.base_models import APIResponse
from models.base_models import EAPIResponseCode
from models.manifest_sql import DataAttributeModel
from models.manifest_sql import DataManifestModel
from resources.error_handler import catch_internal

router = APIRouter()
_logger = LoggerFactory('api_files').get_logger()

_API_NAMESPACE = 'file_entity_restful'


@cbv(router)
class CreateFile:
    def __init__(self):
        self._logger = LoggerFactory('api_file').get_logger()

    @router.post('/', response_model=models.CreateFilePOSTResponse, summary='Create file')
    @catch_internal(_API_NAMESPACE)
    def post(self, data: models.CreateFilePOST):
        api_response = models.CreateFilePOSTResponse()
        self._logger.info(f'file data payload: {data}')
        full_path = data.full_path
        original_geid = data.original_geid
        payload = data.__dict__.copy()
        self._logger.info(f'file payload: {payload}')
        payload['name'] = os.path.basename(full_path)
        payload['path'] = os.path.dirname(full_path)
        payload['archived'] = False

        process_pipeline = payload.get('process_pipeline', None)

        es_payload = {
            'global_entity_id': payload['global_entity_id'],
            'data_type': 'File',
            'operator': payload['uploader'],
            'file_size': payload['file_size'],
            'tags': payload['tags'],
            'archived': False,
            'location': payload['location'],
            'time_lastmodified': time.time(),
            'process_pipeline': payload['process_pipeline'],
            'uploader': payload['uploader'],
            'file_name': payload['name'],
            'time_created': time.time(),
            'atlas_guid': payload['guid'],
            'full_path': payload['full_path'],
            'display_path': payload['display_path'],
            "dcm_id": payload['dcm_id'],
            'project_code': payload['project_code'],
            'list_priority': 20,
        }

        if 'version_id' in payload:
            es_payload['version'] = payload['version_id']

        if data.input_file_id:
            del payload['input_file_id']
            if not data.process_pipeline:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = 'Missing required field process_pipeline for input_file_id'
                return api_response.json_response()
            if not data.operator:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = 'Missing required field operator for input_file_id'
                return api_response.json_response()

        extra_labels = []
        if data.namespace == 'greenroom':
            extra_labels.append('Greenroom')
            es_payload['zone'] = 'Greenroom'
        else:
            extra_labels.append('Core')
            es_payload['zone'] = 'Core'

        # create neo4j payload
        neo4j_payload = {
            "global_entity_id": payload["global_entity_id"],
            "extra_labels": extra_labels,
            "list_priority": 20,
            "uploader": payload["uploader"],
            "file_size": payload["file_size"],
            "tags": payload["tags"],
            "location": payload["location"],
            "process_pipeline": payload["process_pipeline"],
            "name": payload["name"],
            "guid": payload["guid"],
            "full_path": payload["full_path"],
            "display_path": payload["display_path"],
            "dcm_id": payload["dcm_id"],
            "project_code": payload["project_code"],
            "path": payload["path"],
            "version_id": payload["version_id"],
            "operator": payload["operator"],
            "archived": payload["archived"],
            "parent_folder_geid": payload["parent_folder_geid"],
        }

        # Create node
        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'nodes/File', json=neo4j_payload)

        if response.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f'Neo4j error: {response.json()}'
            return api_response.json_response()
        file_node = response.json()[0]

        self._logger.info(f'File Node: {str(file_node)}')

        if data.parent_folder_geid:
            # Create Folder to File relation
            respon_parent_folder_query = folder_models.http_query_node(
                data.namespace, {'global_entity_id': data.parent_folder_geid}
            )
            if not respon_parent_folder_query.status_code == 200:
                raise (
                    Exception(
                        '[respon_parent_folder_query Error] {} {}'.format(
                            respon_parent_folder_query.status_code, respon_parent_folder_query.text
                        )
                    )
                )
            parent_folder_node = respon_parent_folder_query.json()
            if not parent_folder_node:
                raise (
                    Exception(
                        '[respon_parent_folder_query Error] Not found {} {}'.format(
                            respon_parent_folder_query.status_code, data.parent_folder_geid
                        )
                    )
                )
            parent_folder_node = parent_folder_node[0]
            relation_payload = {'start_id': parent_folder_node['id'], 'end_id': file_node['id']}

            with httpx.Client() as client:
                response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/own', json=relation_payload)

            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f'Neo4j error: {response.json()}'
                return api_response.json_response()
        else:
            # Create Container to file relation
            query_params = {'code': data.project_code}
            container_id = get_container_id(query_params)
            # relation_payload = {"start_id": data.project_id,
            #                     "end_id": file_node["id"]}
            relation_payload = {'start_id': container_id, 'end_id': file_node['id']}

            with httpx.Client() as client:
                response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/own', json=relation_payload)
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f'Neo4j error: {response.json()}'
                return api_response.json_response()

        # Create input to processed relation
        # curretly wouldn't be triggered by dataops_util
        if data.input_file_id:
            relation_payload = {
                'start_id': data.input_file_id,
                'end_id': file_node['id'],
                'properties': {'operator': data.operator},
            }
            self._logger.debug('CreateFile relation_payload: ' + str(relation_payload))
            with httpx.Client() as client:
                response = client.post(
                    ConfigClass.NEO4J_SERVICE_V1 + f'relations/{data.process_pipeline}', json=relation_payload
                )
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f'Neo4j error: {response.json()}'
                return api_response.json_response()

        # Create entity in Elastic Search
        if process_pipeline != 'data_delete':
            try:
                if process_pipeline == 'data_transfer' and original_geid:
                    with httpx.Client() as client:
                        response = client.post(
                            ConfigClass.NEO4J_SERVICE_V1 + 'nodes/File/query', json={'global_entity_id': original_geid}
                        )
                    gr_file_node = response.json()[0]
                    self._logger.info(f'Greenroom File Node: {str(gr_file_node)}')
                    if 'manifest_id' in gr_file_node:
                        manifest_id = gr_file_node['manifest_id']
                        full_path = gr_file_node['full_path']

                        attributes = []
                        with httpx.Client() as client:
                            res = client.get(ConfigClass.NEO4J_SERVICE_V1 + f'manifest/{manifest_id}')
                        if res.status_code == 200:
                            manifest_data = res.json()
                            manifest = manifest_data['result']
                            sql_attributes = manifest['attributes']

                            for sql_attribute in sql_attributes:
                                attribute_value = gr_file_node.get('attr_' + sql_attribute['name'], '')

                                if sql_attribute['type'] == 'multiple_choice':
                                    attribute_value = []
                                    attribute_value.append(gr_file_node.get('attr_' + sql_attribute['name'], ''))

                                attributes.append(
                                    {
                                        'attribute_name': sql_attribute['name'],
                                        'name': manifest['name'],
                                        'value': attribute_value,
                                    }
                                )
                        es_payload['attributes'] = attributes
            except Exception as e:
                self._logger.error(str(e))

            self._logger.info('es_payload: ' + str(es_payload))
            with httpx.Client() as client:
                es_res = client.post(ConfigClass.PROVENANCE_SERVICE_V1 + 'entity/file', json=es_payload)
            self._logger.info(f'Elastic Search Result: {es_res.json()}')
            if es_res.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f'Elastic Search Error: {es_res.json()}'
                return api_response.json_response()

        api_response.result = file_node
        return api_response.json_response()


@cbv(router)
class DatasetFileQuery:
    # @router.post('/{dataset_id}/query', response_model=models.DatasetFileQueryPOSTResponse,
    # summary="Query on files by dataset")
    @router.post(
        '/{project_geid}/query',
        response_model=models.DatasetFileQueryPOSTResponse,
        summary='Query on files by Container',
    )
    # def post(self, dataset_id, data: models.DatasetFileQueryPOST):
    def post(self, project_geid, data: models.DatasetFileQueryPOST):
        api_response = models.DatasetFileQueryPOSTResponse()
        page = data.page
        page_size = data.page_size
        order_type = data.order_type
        if order_type and not order_type.lower() in ['desc', 'asc']:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'Invalid order_type'
            return api_response.json_response()
        page_kwargs = {
            'order_by': data.order_by,
            'order_type': order_type,
            'skip': page * page_size,
            'limit': page_size,
        }
        query = data.query
        labels = query.pop('labels', None)
        if not labels:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'Missing required attribute labels'
            return api_response.json_response()

        if not query:
            query = None
        query_params = {'global_entity_id': project_geid}
        container_id = get_container_id(query_params)
        relation_payload = {
            **page_kwargs,
            'label': 'own',
            'start_label': 'Container',
            'end_label': labels,
            'start_params': {'id': int(container_id)},
            'end_params': query,
            'partial': data.partial,
        }
        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/query', json=relation_payload)
        nodes = [x['end_node'] for x in response.json()]

        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/query/count', json=relation_payload)
        total = response.json()['count']
        api_response.result = nodes
        api_response.total = total
        api_response.page = page
        api_response.num_of_pages = math.ceil(total / page_size)
        return api_response.json_response()


@cbv(router)
class TrashCreate:
    def __init__(self):
        self._logger = LoggerFactory('api_delete_file').get_logger()

    @router.post('/trash', response_model=models.CreateTrashPOSTResponse, summary='Create TrashFile')
    def post(self, data: models.CreateTrashPOST):
        api_response = models.CreateTrashPOSTResponse()
        full_path = data.full_path
        trash_full_path = data.trash_full_path
        name = os.path.basename(trash_full_path)
        trash_path = os.path.dirname(trash_full_path)

        self._logger.info('global_entity_id: ' + data.geid)

        # Get existing File
        if data.geid:
            payload = {'global_entity_id': data.geid}
        else:
            payload = {'full_path': data.full_path}

        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'nodes/File/query', json=payload)
        file_node = response.json()[0]
        labels = file_node.get('labels')
        labels.remove('File')

        trash_file_data = {
            'name': name,
            'path': trash_path,
            'full_path': trash_full_path,
            'description': file_node.get('description'),
            'file_size': file_node.get('file_size'),
            'guid': file_node.get('guid'),
            'manifest_id': file_node.get('manifest_id', None),
            'dcm_id': file_node.get('dcm_id', None),
            'archived': True,
            'extra_labels': labels,
            'uploader': file_node.get('uploader'),
            'tags': file_node.get('tags'),
            'global_entity_id': data.trash_geid,
        }

        for key, value in file_node.items():
            if key.startswith('attr_'):
                trash_file_data[key] = value

        # Create TrashFile
        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE_V1 + 'nodes/TrashFile', json=trash_file_data)
        trash_file = response.json()[0]

        # Get dataset
        get_connected = ConfigClass.NEO4J_SERVICE_V1 + 'relations/connected/{}'.format(file_node['global_entity_id'])
        with httpx.Client() as client:
            response = client.get(get_connected)
        connected_nodes = response.json()['result']
        dataset = [connected for connected in connected_nodes if 'Container' in connected['labels']][0]
        container_id = dataset['id']

        # Create File to TrashFile relation
        relation_payload = {
            'start_id': file_node['id'],
            'end_id': trash_file['id'],
            'properties': {'operator': file_node.get('operator')},
        }

        with httpx.Client() as client:
            client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/deleted', json=relation_payload)
        # Create Container to file relation
        relation_payload = {'start_id': container_id, 'end_id': trash_file['id']}

        with httpx.Client() as client:
            client.post(ConfigClass.NEO4J_SERVICE_V1 + 'relations/own', json=relation_payload)
        api_response.result = trash_file

        # Update Elastic Search Entity
        es_payload = {
            'global_entity_id': file_node['global_entity_id'],
            'updated_fields': {
                'name': name,
                'path': trash_path,
                'full_path': trash_full_path,
                'archived': True,
                'process_pipeline': 'data_delete',
                'time_lastmodified': time.time(),
            },
        }
        self._logger.info(f'es delete file payload: {es_payload}')
        with httpx.Client() as client:
            es_res = client.put(ConfigClass.PROVENANCE_SERVICE_V1 + 'entity/file', json=es_payload)
        self._logger.info(f'es delete file response: {es_res.text}')
        if es_res.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f'Elastic Search Error: {es_res.json()}'
            return api_response.json_response()

        return api_response.json_response()


@cbv(router)
class FileManifest:
    # @router.put('/file/manifest', response_model=manifest.PUTAttachResponse, summary="Edit attached manifest")
    @router.put(
        '/{file_geid}/manifest',
        response_model=manifest.PUTAttachResponse,
        summary='Edit attached manifest',
        tags=['files'],
    )
    def put(
        self,
        request: dict,
        file_geid: str,
    ):
        api_response = APIResponse()
        data = request

        # file_node = get_file_node_bygeid(data["global_entity_id"])
        file_node = get_file_node_bygeid(file_geid)
        # data.pop("global_entity_id")
        manifest_obj = db.session.query(DataManifestModel).get(file_node['manifest_id'])

        # Check required attributes
        attributes = (
            db.session.query(DataAttributeModel)
            .filter_by(manifest_id=file_node['manifest_id'])
            .order_by(DataAttributeModel.id.asc())
        )
        valid_attributes = []
        es_attributes = []
        for attr in attributes:
            valid_attributes.append(attr.name)
            if not attr.optional and not attr.name in data:
                api_response.result = 'Missing required attribute'
                api_response.code = EAPIResponseCode.bad_request
                return api_response.json_response()
            if attr.type.value == 'multiple_choice':
                if not data[attr.name] in attr.value.split(','):
                    if not data[attr.name] and attr.optional:
                        continue
                    api_response.result = 'Invalid attribute value'
                    api_response.code = EAPIResponseCode.bad_request
                    _logger.error(api_response.result)
                    return api_response.json_response()
                attribute_value = []
                attribute_value.append(data[attr.name])
                es_attributes.append({'attribute_name': attr.name, 'name': manifest_obj.name, 'value': attribute_value})
            if attr.type.value == 'text':
                value = data[attr.name]
                if value:
                    if len(value) > 100:
                        api_response.result = 'text to long'
                        api_response.code = EAPIResponseCode.bad_request
                        _logger.error(api_response.result)
                        return api_response.json_response()
                    es_attributes.append({'attribute_name': attr.name, 'name': manifest_obj.name, 'value': value})
        post_data = {
            'manifest_id': file_node['manifest_id'],
        }
        for key, value in data.items():
            if key not in valid_attributes:
                api_response.result = 'Not a valid attribute'
                api_response.code = EAPIResponseCode.bad_request
                _logger.error(api_response.result)
                return api_response.json_response()
            post_data['attr_' + key] = value

        file_id = file_node['id']
        with httpx.Client() as client:
            response = client.put(ConfigClass.NEO4J_SERVICE_V1 + f'nodes/File/node/{file_id}', json=post_data)
        api_response.result = response.json()[0]

        # Update Elastic Search Entity
        es_payload = {
            'global_entity_id': file_node['global_entity_id'],
            'updated_fields': {'attributes': es_attributes, 'time_lastmodified': time.time()},
        }
        with httpx.Client() as client:
            es_res = client.put(ConfigClass.PROVENANCE_SERVICE_V1 + 'entity/file', json=es_payload)
        if es_res.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f'Elastic Search Error: {es_res.json()}'
            _logger.error(api_response.error_msg)
            return api_response.json_response()

        return api_response.json_response()


@cbv(router)
class ValidateManifest:
    @router.post(
        '/manifest/validate',
        response_model=manifest.POSTValidateResponse,
        summary='Validate the input to attach a file manifest',
    )
    def post(self, data: manifest.POSTValidateRequest):
        api_response = APIResponse()
        manifest_name = data.manifest_name
        project_code = data.project_code
        manifest = db.session.query(DataManifestModel).filter_by(project_code=project_code, name=manifest_name).first()
        if not manifest:
            api_response.code = EAPIResponseCode.not_found
            api_response.result = f'Manifest not found'
            _logger.error(api_response.result)
            return api_response.json_response()

        attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest.id)
        valid_attributes = []
        for attr in attributes:
            valid_attributes.append(attr.name)

        attributes = data.attributes or {}
        for key, value in attributes.items():
            if key not in valid_attributes:
                api_response.code = EAPIResponseCode.bad_request
                api_response.result = 'Invalid attribute'
                _logger.error(api_response.result)
                return api_response.json_response()

        valid, error_msg = check_attributes(attributes)
        if not valid:
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = error_msg
            _logger.error(api_response.result)
            return api_response.json_response()

        # Check required attributes
        valid, error_msg = has_valid_attributes(manifest.id, data.__dict__)
        if not valid:
            api_response.result = error_msg
            api_response.code = EAPIResponseCode.bad_request
            _logger.error(api_response.result)
            return api_response.json_response()
        api_response.result = 'Success'
        return api_response.json_response()
