from typing import List, Optional, Type, Callable, NoReturn, Literal
from typing_extensions import Self
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
from OMOPSQLModelGen.post_processing_funcs.rename_table_vars import (
    rename_table_variable_names,
)
from OMOPSQLModelGen.post_processing_funcs.replace_temp_pk_with_candidate_keys import (
    replace_temp_pks_with_candidate_keys,
)


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
    pre_generation_sql_script_dirs: Optional[List[Path]] = Field(
        default=None,
        description="If given any sql script in the given directories will be run against the OMOP refernce database. this will happen before we generate the python models.",
    )
    post_generation_python_functions: Optional[
        List[
            Callable[
                [
                    Path,
                    Self,
                    Literal["tables", "declarative", "dataclasses", "sqlmodels"],
                ],
                NoReturn,
            ]
        ]
    ] = Field(
        default=None,
        description="If given these python functions will be called  after the each flavor of python model were generated. The function will be called wit This can be used for rework on the generated code.",
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
    pre_generation_sql_script_dirs=[
        "OMOPSQLModelGen/pre_gen_sql/5.x/",
        "OMOPSQLModelGen/pre_gen_sql/5.3/",
    ],
    post_generation_python_functions=[
        rename_table_variable_names,
        replace_temp_pks_with_candidate_keys,
    ],
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
    pre_generation_sql_script_dirs=[
        "OMOPSQLModelGen/pre_gen_sql/5.x/",
        "OMOPSQLModelGen/pre_gen_sql/5.4/",
    ],
)

SOURCES: List[OMOPSchemaSource] = omopcdm_5_3, omopcdm_5_4
