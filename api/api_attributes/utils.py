import requests 
from config import ConfigClass
import time

def get_files_recursive(folder_geid, all_files=[]):
    query = {
        "start_label": "Folder",
        "end_labels": ["File", "Folder"],
        "query": {
            "start_params": {
                "global_entity_id": folder_geid,
            },
            "end_params": {
                "archived": False
            }
        }
    }
    

    resp = requests.post(ConfigClass.NEO4J_SERVICE_V2 + "relations/query", json=query)
    for node in resp.json()["results"]:
        if "File" in node["labels"]:
            all_files.append(node)
        else:
            get_files_recursive(node["global_entity_id"], all_files=all_files)
    
    return all_files


def get_file_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/File/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0] 


def get_folder_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/Folder/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0] 

def is_valid_file(file_node, project_role, username):
    if file_node['archived'] == True:
        return False
    elif project_role != 'admin':
        if project_role == 'contributor' and file_node['uploader'] != username:
            return False
        elif project_role == 'collaborator':
            if "VRECore" not in file_node['labels'] and file_node['uploader'] != username:
                return False    
            return True
        else:
            return True
    else:
        return True

def has_valid_attributes(attributes, received_attributes):
    for attr in attributes:
        if not attr["optional"] and not attr["name"] in received_attributes:
            return False, "Missing required attribute"
        if attr["type"] == "multiple_choice":
            value = received_attributes.get(attr["name"])
            if value:
                if not value in attr["value"].split(","):
                    return False, "Invalid choice field"
            else:
                if not attr["optional"]:
                    return False, "Field required"
        if attr["type"] == "text":
            value = received_attributes.get(attr["name"])
            if value:
                if len(value) > 100:
                    return False, "text too long"
            else:
                if not attr["optional"]:
                    return False, "Field required"
    return True, ""


def attach_attributes(manifest, attributes, file_node, _logger):
    post_data = {
        "manifest_id": manifest['id'],
    }

    sql_attributes = manifest['attributes']

    es_attributes = []

    for key in attributes:
        value = attributes[key]
        post_data["attr_" + key] = value

        sql_attribute = [x for x in sql_attributes if x['name'] == key]
        if len(sql_attribute) == 0:
            continue
        sql_attribute = sql_attribute[0]

        if sql_attribute["type"] == 'multiple_choice':
            attribute_value = []
            attribute_value.append(value)

            es_attributes.append({
                "attribute_name": key,
                "name": manifest['name'],
                "value": attribute_value
            })
        else:
            es_attributes.append({
                "attribute_name": key,
                "name": manifest['name'],
                "value": value
            })
    file_id = file_node["id"]
    response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/File/node/{file_id}", json=post_data)

    if response.status_code != 200:
        _logger.error('Update Neo4j Node failed: {}'.format(response.text))
        return False

    # Update Elastic Search Entity
    es_payload = {
        "global_entity_id": file_node["global_entity_id"],
        "updated_fields": {
            "attributes": es_attributes,
            "time_lastmodified": time.time()
        }
    }
    es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_payload)

    if es_res.status_code != 200:
        _logger.error('Update Elastic Search Entity failed: {}'.format(es_res.text))
        return False

    return True