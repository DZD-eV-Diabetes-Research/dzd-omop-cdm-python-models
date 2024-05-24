from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    Field,
    AnyUrl,
    SecretStr,
    AnyHttpUrl,
    StringConstraints,
    model_validator,
)
from typing import List, Annotated, Optional, Literal, Dict
from pathlib import Path, PurePath
from textwrap import dedent


env_file_path = Path(__file__).parent / ".env"
print("env_file_path", env_file_path.resolve())


class Config(BaseSettings):
    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(
        default="INFO"
    )
    OMOP_CDM_RELEASE_FILE: AnyHttpUrl = Field(
        description="Link to the source code archive (zip) of a github release. This will be the base data for the OMOP SQLModel Python Package that is gona be generated. See https://github.com/OHDSI/CommonDataModel/releases for all releases. Provide the link to the 'Source Code (Zip) file'",
        default="https://github.com/OHDSI/CommonDataModel/archive/refs/tags/v5.4.1.zip",
    )
    OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR: Path = Field(
        default=Path("./downloads/CommonDataModel-5.4.1"),
        descricption="The file from OMOP_CDM_RELEASE_FILE will be downloaded and extracted into this dir.",
    )
    POSTGRESQL_HOST: str = Field(default="localhost")
    POSTGRESQL_USER: str = Field(default="omop")
    POSTGRESQL_DATABASE: str = Field(default="omop")
    POSTGRESQL_PASSWORD: str = Field(default="omop")
    POSTGRESQL_PORT: int = Field(default=5432)
    POSTGRESQL_SCHEMA: str = Field(default="public")

    def get_sql_url(self):
        return f"postgresql+pg8000://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}@{self.POSTGRESQL_HOST}/{self.POSTGRESQL_DATABASE}"

    SQLACODEGEN_GENERATOR: Literal[
        "tables", "declarative", "dataclasses", "sqlmodels"
    ] = Field(
        default="declarative",
        description="The class style that should be genrated. https://github.com/agronholm/sqlacodegen SQLModel is blocked atm due to https://github.com/agronholm/sqlacodegen/pull/306 (sqlcodegen 3.0.0rc5. Should be fixed in next release.)",
    )
    DATAMODEL_OUTPUT_DIR: Path = Field(default="./OMOPModel")

    OMOP_SQL_SCRIPT_SCHEMA_PLACEHOLDER_STRING: str = Field(
        default="@cdmDatabaseSchema",
        description="All official OMOP SQL script, contain a placeholder string, which needs to be replaced with the actual database schema name. Usually you wont ever need to changes this setting.",
    )

    ###### CONFIG END ######
    # class Config is a pydantic-settings pre-defined config class to control the behaviour of our settings model
    # if you dont know what this is you can ignore it.
    # https://docs.pydantic.dev/latest/api/base_model/#pydantic.main.BaseModel.model_config

    class Config:
        env_nested_delimiter = "__"
        env_file = env_file_path
        env_file_encoding = "utf-8"
