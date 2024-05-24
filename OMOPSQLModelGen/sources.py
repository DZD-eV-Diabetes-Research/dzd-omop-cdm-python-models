from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    SecretStr,
    AnyHttpUrl,
    validator,
    StringConstraints,
    model_validator,
)
from pathlib import Path


class OMOPSchemaSource(BaseModel):
    version_name: str
    sql_constraints_file_path: Path = Field(
        description="The relative path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql constraints."
    )
    sql_ddl_file_path: Path = Field(
        description="The relative path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql tables."
    )
    sql_indices_file_path: Path = Field(
        description="The relative path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql indices."
    )
    sql_primary_keys_file_path: Path = Field(
        description="The relative path to the sql script file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') for sql primary keys."
    )
    csv_table_desc_file_path: Path = Field(
        description="The relative path to the CSV file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') which contains a description of all tables."
    )
    csv_field_desc_file_path: Path = Field(
        description="The relative path to the CSV file in the OMOP release archive (As defined in the config var 'OMOP_CDM_RELEASE_FILE') which contains a description of all fields."
    )


omopcdm_5_3 = OMOPSchemaSource(
    version_name="OMOP_CDM_5.3",
    sql_constraints_file_path=Path(
        "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_constraints.sql"
    ),
    sql_ddl_file_path=Path("inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_ddl.sql"),
    sql_indices_file_path=Path(
        "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_indices.sql"
    ),
    sql_primary_keys_file_path=Path(
        "inst/ddl/5.3/postgresql/OMOPCDM_postgresql_5.3_primary_keys.sql"
    ),
    csv_table_desc_file_path=Path("inst/csv/OMOP_CDMv5.3_Table_Level.csv"),
    csv_field_desc_file_path=Path("inst/csv/OMOP_CDMv5.3_Field_Level.csv"),
)
