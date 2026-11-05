from typing import List, Optional, Type, Callable, NoReturn, Literal
from typing_extensions import Self
from pydantic import (
    BaseModel,
    Field,
)
from pathlib import Path
from config import Config

config = Config()
from OMOPSQLModelGen.post_processing_funcs.rename_table_vars import (
    rename_table_variable_names,
)
from OMOPSQLModelGen.post_processing_funcs.replace_temp_pk_with_candidate_keys import (
    replace_temp_pks_with_candidate_keys,
)
from OMOPSQLModelGen.post_processing_funcs.fix_sql_model import (
    fix_sql_model,
)
from OMOPSQLModelGen.post_processing_funcs.fix_death_table_glitch import (
    fix_death_table_glitch,
)
from OMOPSQLModelGen.post_processing_funcs.remove_reverse_1to1 import (
    remove_reverse_1to1,
)
from OMOPSQLModelGen.post_processing_funcs.remove_excessive_backpopulate import (
    remove_excessive_backpopulate,
)
from OMOPSQLModelGen.post_processing_funcs.add_pural_names_to_back_populating_lists import (
    pluralize_names_of_list_attributes,
)
from OMOPSQLModelGen.post_processing_funcs.add_license import (
    add_license,
)


class OMOPSchemaSource(BaseModel):
    version_name: str
    base_path: Path = None
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
    version_name="OMOP_5_3",
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
    pre_generation_sql_script_dirs=[
        "pre_gen_sql/5.x/",
        "pre_gen_sql/5.3/",
    ],
    post_generation_python_functions=[
        rename_table_variable_names,
        replace_temp_pks_with_candidate_keys,
        #fix_sql_model,
        fix_death_table_glitch,
        remove_reverse_1to1,
        remove_excessive_backpopulate,
        pluralize_names_of_list_attributes,
        add_license,
    ],
)


omopcdm_5_4 = OMOPSchemaSource(
    version_name="OMOP_5_4",
    sql_constraints_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_constraints.sql"
    ),
    sql_ddl_file_path=Path("inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql"),
    sql_indices_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_indices.sql"
    ),
    sql_primary_keys_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_primary_keys.sql"
    ),
    csv_table_desc_file_path=Path("inst/csv/OMOP_CDMv5.4_Table_Level.csv"),
    csv_field_desc_file_path=Path("inst/csv/OMOP_CDMv5.4_Field_Level.csv"),
    pre_generation_sql_script_dirs=[
        "pre_gen_sql/5.x/",
        "pre_gen_sql/5.4/",
    ],
    post_generation_python_functions=[
        rename_table_variable_names,
        replace_temp_pks_with_candidate_keys,
        #fix_sql_model,
        fix_death_table_glitch,
        remove_reverse_1to1,
        remove_excessive_backpopulate,
        pluralize_names_of_list_attributes,
        add_license,
    ],
)

omopcdm_6_0 = OMOPSchemaSource(
    version_name="OMOP_6_0",
    sql_constraints_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_constraints.sql"
    ),
    sql_ddl_file_path=Path("inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql"),
    sql_indices_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_indices.sql"
    ),
    sql_primary_keys_file_path=Path(
        "inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_primary_keys.sql"
    ),
    csv_table_desc_file_path=Path("inst/csv/OMOP_CDMv5.4_Table_Level.csv"),
    csv_field_desc_file_path=Path("inst/csv/OMOP_CDMv5.4_Field_Level.csv"),
    pre_generation_sql_script_dirs=[
        "pre_gen_sql/5.x/",
        "pre_gen_sql/5.4/",
    ],
    post_generation_python_functions=[
        rename_table_variable_names,
        replace_temp_pks_with_candidate_keys,
        #fix_sql_model,
        fix_death_table_glitch,
        remove_reverse_1to1,
        remove_excessive_backpopulate,
        pluralize_names_of_list_attributes,
        add_license,
    ],
)

SOURCES: List[OMOPSchemaSource] = omopcdm_5_3, omopcdm_5_4
