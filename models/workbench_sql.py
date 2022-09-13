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
from sqlalchemy import Column, String, Date, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from config import ConfigClass

Base = declarative_base()


class WorkbenchModel(Base):
    __tablename__ = 'workbench_resource'
    __table_args__ = {"schema":ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    geid = Column(String())
    project_code = Column(String())
    workbench_resource = Column(String())
    deployed = Column(Boolean())
    deployed_date = Column(DateTime())
    deployed_by = Column(String())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        result = {}
        field_list = [
            "id",
            "geid",
            "project_code",
            "workbench_resource",
            "deployed",
            "deployed_date",
            "deployed_by",
        ]
        for field in field_list:
            if field == "deployed_date":
                value = getattr(self, field)
                if value:
                    result[field] = value.isoformat()
            else:
                result[field] = getattr(self, field)
        return result
