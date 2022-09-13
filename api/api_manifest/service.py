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

from fastapi_sqlalchemy import db
from models.manifest_sql import DataManifestModel , DataAttributeModel

class Manifest:

    @classmethod
    def get_by_project_name(cls, project_code):
        manifests = db.session.query(DataManifestModel).filter_by(project_code=project_code)
        results = []
        for manifest in manifests:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(
                manifest_id=manifest.id
            ).order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            results.append(result)
        return results

    @classmethod
    def get_by_id(cls, id):
        manifest = db.session.query(DataManifestModel).get(id)
        if manifest:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(
                manifest_id=id
            ).order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            return result
        return None