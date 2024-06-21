import sys, os
from pathlib import Path, PurePath

import subprocess

# At this module as a register python module. This will make dev-imports in other files easier.
if __name__ == "__main__":
    from pathlib import Path
    import sys, os

    MODULE_DIR = Path(__file__).parent
    MODULE_PARENT_DIR = MODULE_DIR.parent.absolute()
    sys.path.insert(0, os.path.normpath(MODULE_PARENT_DIR))


from OMOPSQLModelGen.reference_database_handler import ReferencePostgresHandler
from OMOPSQLModelGen.sources import SOURCES
from OMOPSQLModelGen.omop_cdm_release_downloader import OMOPCDMReleaseDownloader
from OMOPSQLModelGen.pre_generation_processes import run_pre_sql_scripts
from OMOPSQLModelGen.config import Config

config = Config()
OMOPCDMReleaseDownloader().download(
    force_redownload=config.FORCE_REDOWNLOAD_OMOP_CDM_RELEASE
)
for OMOP_source in SOURCES:
    print("config.POSTGRESQL_DATABASE", config.POSTGRESQL_DATABASE)
    db = ReferencePostgresHandler(
        db_host=config.POSTGRESQL_HOST,
        db_name=config.POSTGRESQL_DATABASE,
        db_user=config.POSTGRESQL_USER,
        db_password=config.POSTGRESQL_PASSWORD,
        db_port=config.POSTGRESQL_PORT,
    )
    db.create_omop_schema(omop_schema_source=OMOP_source, wipe_clean_before=True)
    db.enrich_omop_schema_metadata(omop_schema_source=OMOP_source)
    # pre sql scripts
    run_pre_sql_scripts(db, OMOP_source)

    for data_class_style in config.SQLACODEGEN_GENERATORS:
        sqlqcodegan_cmd = (
            f"""sqlacodegen --generator {data_class_style} {config.get_sql_url()}"""
        )
        print(f"RUN: {sqlqcodegan_cmd}")
        cmd = [
            "bash",
            "-c",
            sqlqcodegan_cmd,
        ]
        output_file_path = Path(
            PurePath(
                config.DATAMODEL_OUTPUT_DIR,
                f"{OMOP_source.version_name}_{data_class_style}.py",
            )
        )
        if not output_file_path:
            print(f"Something went wrong with {sqlqcodegan_cmd}")
            continue
        config.DATAMODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # remove file if already exists:
        output_file_path.unlink(missing_ok=True)
        # run command and output to file
        with open(output_file_path, "w") as out:
            return_code = subprocess.call(cmd, stdout=out)
            print("return_code", return_code)
        if OMOP_source.post_generation_python_functions:
            for post_processing_func in OMOP_source.post_generation_python_functions:

                print(
                    f"Run post processing function '{post_processing_func.__name__}' on file '{output_file_path.absolute()}'"
                )
                post_processing_func(output_file_path, OMOP_source, data_class_style)

    # sqlacodegen --generator sqlmodel postgresql://ps:ps@localhost/ps
