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

from app import app
import pytest
from fastapi.testclient import TestClient
from models.manifest_sql import Base as ManifestBase
from models.manifest_sql import DataManifestModel
from models.manifest_sql import DataAttributeModel
from models.metrics_sql import Base as MetricsBase
from models.metrics_sql import SystemMetrics
from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import Session
from datetime import datetime
import os
from testcontainers.postgres import PostgresContainer
from config import ConfigClass
from fastapi_sqlalchemy import DBSessionMiddleware

RDS_DB_URI = os.environ['RDS_DB_URI']
RDS_SCHEMA_DEFAULT = os.environ['RDS_SCHEMA_DEFAULT']


@pytest.fixture(scope='session')
def db():
    with PostgresContainer("postgres:9.5") as postgres:
        postgres.get_connection_url()
        yield postgres


@pytest.fixture
def test_client(db):
    ConfigClass.RDS_DB_URI = db.get_connection_url()
    app.add_middleware(DBSessionMiddleware, db_url=ConfigClass.RDS_DB_URI)
    client = TestClient(app)
    return client


@pytest.fixture
def create_db_system_metrics(db):
    engine = create_engine(db.get_connection_url())
    CreateTable(SystemMetrics.__table__).compile(dialect=postgresql.dialect())
    MetricsBase.metadata.create_all(bind=engine)
    s = Session(engine)
    s.add(SystemMetrics(active_user=100, project=20, storage=150, vm=10, cores=20, ram=200,
                        date=datetime(2022, 2, 9, 15, 36, 0)))
    s.commit()
    yield
    MetricsBase.metadata.drop_all(bind=engine)


@pytest.fixture
def create_db_manifest(db):
    engine = create_engine(db.get_connection_url())
    if not engine.dialect.has_schema(engine, RDS_SCHEMA_DEFAULT):
        engine.execute(CreateSchema(RDS_SCHEMA_DEFAULT))
    CreateTable(DataManifestModel.__table__).compile(dialect=postgresql.dialect())
    CreateTable(DataAttributeModel.__table__).compile(dialect=postgresql.dialect())
    ManifestBase.metadata.create_all(bind=engine)
    s = Session(engine)

    project_code = "testproject"
    s.add(DataManifestModel(name="test123", project_code=project_code))
    s.add(DataManifestModel(name="test1234", project_code=project_code))
    s.commit()
    s.add(DataAttributeModel(manifest_id=1, name="test123", type="text", value="1",
                             project_code=project_code, optional=True))
    s.add(DataAttributeModel(manifest_id=2, name="test1234", type="text", value="100",
                             project_code=project_code, optional=True))
    s.commit()
    yield project_code
    engine.execute("DROP TYPE typeenum CASCADE")
    ManifestBase.metadata.drop_all(bind=engine)
