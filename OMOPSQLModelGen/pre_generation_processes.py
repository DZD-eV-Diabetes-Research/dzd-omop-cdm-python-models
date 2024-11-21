import os, sys
from pathlib import Path

from OMOPSQLModelGen.reference_database_handler import ReferencePostgresHandler
from OMOPSQLModelGen.sources import OMOPSchemaSource
from OMOPSQLModelGen.config import Config

config = Config()


def run_pre_sql_scripts(db: ReferencePostgresHandler, omop_source: OMOPSchemaSource):
    for sql_script_dir in omop_source.pre_generation_sql_script_dirs:
        print("__NAME__", __name__)
        print("os.path.abspath(sys.argv[0])", os.path.abspath(sys.argv[0]))
        sql_script_dir_abs = Path(
            Path(os.path.abspath(sys.argv[0])).parent.absolute(), sql_script_dir
        )
        for obj in sql_script_dir_abs.iterdir():
            if obj.is_file() and obj.suffix.lower() == ".sql":
                print(
                    f"Run sql script '{obj.absolute()}' before model generation (OMOP CDM Source name: {omop_source.version_name})."
                )
                db.run_sql_script_file(obj)
