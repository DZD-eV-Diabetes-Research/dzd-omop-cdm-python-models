"""Settings, read once from env vars (or ``.env`` in the working directory)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

Flavor = Literal["tables", "declarative", "dataclasses", "sqlmodels"]
FLAVORS: tuple[Flavor, ...] = ("tables", "declarative", "dataclasses", "sqlmodels")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"

    OMOP_CDM_RELEASE_TAG: str = Field(
        default="v5.4.1",
        description="Tag of an OHDSI/CommonDataModel release on GitHub. "
        "Its source archive holds the DDL and the CSV specs for every CDM version we generate.",
    )
    OMOP_CDM_DOWNLOAD_DIR: Path = Field(
        default=Path("downloads"),
        description="Cache for release archives. Each tag is extracted into its own subfolder.",
    )
    FORCE_REDOWNLOAD_OMOP_CDM_RELEASE: bool = Field(
        default=False,
        description="Download the release again even when it's already in the cache.",
    )

    POSTGRESQL_HOST: str = "localhost"
    POSTGRESQL_PORT: int = 5432
    POSTGRESQL_USER: str = "omop"
    POSTGRESQL_PASSWORD: SecretStr = SecretStr("omop")
    POSTGRESQL_DATABASE: str = "omop"
    POSTGRESQL_SCHEMA: str = Field(
        default="public",
        description="Schema the DDL is deployed to. WARNING: it is dropped and recreated per CDM version.",
    )

    CDM_VERSIONS: list[str] = Field(
        default=["5.3", "5.4"], description="CDM versions to generate (see cdm_versions.py)."
    )
    FLAVORS: list[Flavor] = Field(
        default=list(FLAVORS), description="Model flavors (sqlacodegen generators) to generate."
    )
    DATAMODEL_OUTPUT_DIR: Path = Field(
        default=Path("packages/dzdomop/src/omopmodel"),
        description="Where the generated OMOP_<version>_<flavor>.py files go.",
    )

    def sql_url(self) -> URL:
        return URL.create(
            "postgresql+pg8000",
            username=self.POSTGRESQL_USER,
            password=self.POSTGRESQL_PASSWORD.get_secret_value(),
            host=self.POSTGRESQL_HOST,
            port=self.POSTGRESQL_PORT,
            database=self.POSTGRESQL_DATABASE,
        )
