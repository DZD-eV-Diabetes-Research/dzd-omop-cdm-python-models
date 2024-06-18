from typing import List, Optional, Type
from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    SecretStr,
    AnyHttpUrl,
    StringConstraints,
    model_validator,
)
from pathlib import Path, PurePath
from config import Config

config = Config()


class OMOPSchemaSource(BaseModel):
    version_name: str
    sql_constraints_file_path: Path = Field(
        description="The path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql constraints."
    )
    sql_ddl_file_path: Path = Field(
        description="The path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql tables."
    )
    sql_indices_file_path: Path = Field(
        description="The path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql indices."
    )
    sql_primary_keys_file_path: Path = Field(
        description="The path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql primary keys."
    )
    csv_table_desc_file_path: Path = Field(
        description="The path to the CSV file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') which contains a description of all tables."
    )
    csv_field_desc_file_path: Path = Field(
        description="The path to the CSV file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') which contains a description of all fields."
    )
    pre_generation_sql_script_dir: Optional[Path] = Field(
        default=None,
        description="If given this sql script will be run against the database, before we generate the models",
    )
    post_generation_python_class: Optional[Type] = Field(
        default=None,
        description="If given this python class will be instanciated and the method `run`will be called. this will happen after model generation.",
    )


omopcdm_5_3 = OMOPSchemaSource(
    version_name="OMOP_CDM_5.3",
    sql_constraints_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_constraints.sql",
        )
    ),
    sql_ddl_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_ddl.sql",
        )
    ),
    sql_indices_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_indices.sql",
        )
    ),
    sql_primary_keys_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_primary_keys.sql",
        )
    ),
    csv_table_desc_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/csv/OMOP_CDMv5.3_Table_Level.csv",
        )
    ),
    csv_field_desc_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/csv/OMOP_CDMv5.3_Field_Level.csv",
        )
    ),
    pre_generation_sql_script_dir="OMOPSQLModelGen/pre_gen_sql/5.x/add_missing_primary_keys.sql",
)


omopcdm_5_4 = OMOPSchemaSource(
    version_name="OMOP_CDM_5.4",
    sql_constraints_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_constraints.sql",
        )
    ),
    sql_ddl_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql",
        )
    ),
    sql_indices_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_indices.sql",
        )
    ),
    sql_primary_keys_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_primary_keys.sql",
        )
    ),
    csv_table_desc_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/csv/OMOP_CDMv5.4_Table_Level.csv",
        )
    ),
    csv_field_desc_file_path=Path(
        PurePath(
            config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
            "inst/csv/OMOP_CDMv5.4_Field_Level.csv",
        )
    ),
    pre_generation_sql_script_dir="OMOPSQLModelGen/pre_gen_sql/5.x/add_missing_primary_keys.sql",
)

SOURCES: List[OMOPSchemaSource] = omopcdm_5_3, omopcdm_5_4
