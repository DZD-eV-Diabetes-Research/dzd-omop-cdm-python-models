import sys, os
from pathlib import Path, PurePath
from config import Config
import subprocess

# At this module as a register python module. This will make dev-imports in other files easier.
if __name__ == "__main__":
    from pathlib import Path
    import sys, os

    MODULE_DIR = Path(__file__).parent
    MODULE_PARENT_DIR = MODULE_DIR.parent.absolute()
    sys.path.insert(0, os.path.normpath(MODULE_PARENT_DIR))


from OMOPSQLModelGen.reference_database_handler import ReferencePostgresHandler
from OMOPSQLModelGen.sources import omopcdm_5_3


config = Config()
print("config.POSTGRESQL_DATABASE", config.POSTGRESQL_DATABASE)
db = ReferencePostgresHandler(
    db_host=config.POSTGRESQL_HOST,
    db_name=config.POSTGRESQL_DATABASE,
    db_user=config.POSTGRESQL_USER,
    db_password=config.POSTGRESQL_PASSWORD,
    db_port=config.POSTGRESQL_PORT,
)
db.create_omop_schema(omop_schema_source=omopcdm_5_3, wipe_clean_before=True)
db.enrich_omop_schema_metadata(omop_schema_source=omopcdm_5_3)

cmd = [
    "bash",
    "-c",
    f"sqlacodegen --generator {config.SQLACODEGEN_GENERATOR} {config.get_sql_url()}",
]
output = Path(PurePath(config.DATAMODEL_OUTPUT_DIR, f"{omopcdm_5_3.version_name}.py"))
config.DATAMODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with open(output, "w") as out:
    return_code = subprocess.call(cmd, stdout=out)
    print("return_code", return_code)

# sqlacodegen --generator sqlmodel postgresql://ps:ps@localhost/ps
