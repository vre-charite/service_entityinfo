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

from functools import lru_cache
from typing import Any
from typing import Dict

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra
from starlette.config import Config

config = Config('.env')
SRV_NAMESPACE = config('APP_NAME', cast=str, default='service_metadata')
CONFIG_CENTER_ENABLED = config('CONFIG_CENTER_ENABLED', cast=str, default='false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(config('VAULT_URL'), config('VAULT_CRT'), config('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'service_metadata'
    PORT: int = 5066
    HOST: str = '127.0.0.1'
    env: str = ''
    namespace: str = SRV_NAMESPACE

    NEO4J_SERVICE: str
    ENTITYINFO_SERVICE: str
    PROVENANCE_SERVICE: str
    UTILITY_SERVICE: str
    DATA_OPS_UTIL: str
    CATALOGUING_SERVICE: str

    RDS_DB_URI: str
    RDS_SCHEMA_DEFAULT: str

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def __init__(self):
        super().__init__()
        self.NEO4J_SERVICE_V1 = self.NEO4J_SERVICE + '/v1/neo4j/'
        self.NEO4J_SERVICE_V2 = self.NEO4J_SERVICE + '/v2/neo4j/'
        self.PROVENANCE_SERVICE_V1 = self.PROVENANCE_SERVICE + '/v1/'
        self.UTILITY_SERVICE_V1 = self.UTILITY_SERVICE + '/v1/'
        self.DATAOPS = self.DATA_OPS_UTIL
        self.CATALOGUING = self.CATALOGUING_SERVICE

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()
