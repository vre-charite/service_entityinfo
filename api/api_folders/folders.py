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

import json
import math
import os
import time

import httpx
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

from config import ConfigClass
from models import folders as models
from models.base_models import EAPIResponseCode
from models.meta import get_parent_connections
from resources.error_handler import catch_internal

router = APIRouter()
_API_NAMESPACE = 'api_folder_nodes'


@cbv(router)
class FolderNodes:
    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.post('/folders/batch', response_model=models.FoldersPOSTResponse, summary='Batch Folder Nodes Restful')
    # @catch_internal(_API_NAMESPACE)
    def batch_folder(self, request_payload: models.BatchFoldersPOST):
        """Post function to btach create folder."""
        self._logger.info(f'folder payload: {request_payload.__dict__}')
        api_response = models.APIResponse()
        payload = request_payload.payload

        namespace = request_payload.zone
        extra_labels = [namespace]

        nodes_data = []
        relations_data = []

        for item in payload:
            item = dict(item)
            # time_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_node = {
                'global_entity_id': item['global_entity_id'],
                'name': item['folder_name'],
                'folder_level': item['folder_level'],
                'folder_relative_path': item['folder_relative_path'],
                'project_code': item['project_code'],
                'tags': item['folder_tags'],
                'list_priority': 10,
                'uploader': item['uploader'],
                'archived': False,
                'display_path': os.path.join(item['folder_relative_path'], item['folder_name']),
                # "time_created": time_now,
                # "time_lastmodified": time_now
            }
            if 'extra_attrs' in item:
                for k, v in item['extra_attrs'].items():
                    new_node[k] = v

            nodes_data.append(new_node)
            if request_payload.link_container:
                relations_data.append(
                    {
                        'start_params': {'code': new_node['project_code']},
                        'end_params': {
                            'project_code': new_node['project_code'],
                            'global_entity_id': new_node['global_entity_id'],
                        },
                    }
                )

            if not request_payload.link_container and len(new_node['folder_relative_path']):
                self._logger.info('create folder in elastic search')
                try:
                    es_body = {
                        'global_entity_id': new_node['global_entity_id'],
                        'zone': namespace,
                        'data_type': 'Folder',
                        'operator': new_node['uploader'],
                        'file_size': 0,
                        'tags': new_node['tags'],
                        'archived': False,
                        'location': '',
                        'time_lastmodified': time.time(),
                        'process_pipeline': '',
                        'uploader': new_node['uploader'],
                        'file_name': new_node['name'],
                        'time_created': time.time(),
                        'atlas_guid': '',
                        'display_path': new_node['display_path'],
                        'dcm_id': None,
                        'project_code': new_node['project_code'],
                        'priority': 10,
                    }
                    with httpx.Client() as client:
                        es_res = client.post(ConfigClass.PROVENANCE_SERVICE_V1 + 'entity/file', json=es_body)
                    self._logger.info(es_body)
                    self._logger.info(es_res.text)
                    if es_res.status_code != 200:
                        self._logger.error(f'Error while creating folder node in elastic search : {es_res.text}')
                        api_response.code = EAPIResponseCode.internal_error
                        api_response.result = 'Error while creating folder node in elastic search'
                        return api_response.json_response()
                except Exception as e:
                    self._logger.error('Error while call elastic search' + str(e))
                    api_response.code = EAPIResponseCode.internal_error
                    api_response.result = 'Error while call elastic search' + str(e)
                    return api_response.json_response()

        result_create_node = models.http_bulk_post_node(nodes_data, extra_labels)

        if result_create_node.status_code == 200:
            if relations_data:
                result_link_projects = models.bulk_link_project(['start', 'end'], 'Container', 'Folder', relations_data)
                if result_link_projects.status_code == 200:
                    api_response.code = EAPIResponseCode.success
                    api_response.result = {'result': 'success'}
                else:
                    api_response.code = EAPIResponseCode.internal_error
                    api_response.result = {'result': 'failed to link projects with folders'}
        else:
            api_response.code = EAPIResponseCode.internal_error
            api_response.result = {'result': 'failed to create folders'}

        return api_response.json_response()

    @router.post('/folders', response_model=models.FoldersPOSTResponse, summary='Folder Nodes Restful')
    @catch_internal(_API_NAMESPACE)
    def post(self, request_payload: models.FoldersPOST):
        """Post function to create entity."""
        self._logger.info(f'folder payload: {request_payload.__dict__}')
        api_response = models.APIResponse()
        namespace = request_payload.zone
        extra_labels = [namespace]
        extra_labels += request_payload.extra_labels
        new_node = {
            'global_entity_id': request_payload.global_entity_id,
            'name': request_payload.folder_name,
            'folder_level': request_payload.folder_level,
            'folder_relative_path': request_payload.folder_relative_path,
            'project_code': request_payload.project_code,
            'tags': request_payload.folder_tags,
            'list_priority': 10,
            'extra_labels': extra_labels,
            'uploader': request_payload.uploader,
            'archived': False,
            'display_path': os.path.join(request_payload.folder_relative_path, request_payload.folder_name),
        }

        # name folder do not need to be stored in es
        if len(request_payload.folder_relative_path):
            es_body = {
                'global_entity_id': request_payload.global_entity_id,
                'zone': namespace,
                'data_type': 'Folder',
                'operator': request_payload.uploader,
                'file_size': 0,
                'tags': request_payload.folder_tags,
                'archived': False,
                'location': '',
                'time_lastmodified': time.time(),
                'process_pipeline': '',
                'uploader': request_payload.uploader,
                'file_name': request_payload.folder_name,
                'time_created': time.time(),
                'atlas_guid': '',
                'display_path': os.path.join(request_payload.folder_relative_path, request_payload.folder_name),
                'dcm_id': None,
                'project_code': request_payload.project_code,
                'priority': 10,
            }
            with httpx.Client() as client:
                es_res = client.post(ConfigClass.PROVENANCE_SERVICE_V1 + 'entity/file', json=es_body)
            if es_res.status_code != 200:
                self._logger.error(f'Error while creating folder node in elastic search : {es_res.text}')
                api_response.code = EAPIResponseCode.internal_error
                api_response.result = 'Error while creating folder node in elastic search'
                return api_response.json_response()

        is_trashbin_root = request_payload.extra_attrs.get('is_trashbin_root')
        for k, v in request_payload.extra_attrs.items():
            new_node[k] = v
        self._logger.info(f' neo4j folder creation payload:  {new_node}')
        result_create_node = models.http_post_node(new_node, request_payload.global_entity_id)
        if result_create_node.status_code == 200:
            node_created = result_create_node.json()[0]
            # if not root node folder
            if request_payload.folder_relative_path and request_payload.folder_parent_geid and not is_trashbin_root:
                models.link_folder_parent(
                    namespace, request_payload.folder_parent_geid, node_created['global_entity_id']
                )
            else:
                models.link_project(namespace, request_payload.project_code, node_created['global_entity_id'])
            api_response.code = EAPIResponseCode.success
            api_response.result = node_created
            return api_response.json_response()
        else:
            raise (Exception('Create failed' + result_create_node.text))

    @router.get('/folders', response_model=models.FoldersQueryResponse, summary='Folder Nodes Restful')
    @catch_internal(_API_NAMESPACE)
    def query(self, zone, project_code, folder_relative_path=None, uploader=None):
        """Get function to query the entity by condition."""
        api_response = models.APIResponse()
        if not zone in ['core', 'greenroom']:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'Invalid zone parameter'
            return api_response.json_response()
        namespace = {'core': 'Core', 'greenroom': 'Greenroom'}.get(zone)
        query_payload = {'project_code': project_code}
        if folder_relative_path:
            query_payload['folder_relative_path'] = folder_relative_path
        if uploader:
            query_payload['uploader'] = uploader
        query_respon = models.http_query_node(namespace, query_payload)
        if query_respon.status_code == 200:
            api_response.code = EAPIResponseCode.success
            api_response.result = query_respon.json()
            return api_response.json_response()
        else:
            raise (Exception('query_respon: {}, {}'.format(query_respon.status_code, query_respon.text)))
