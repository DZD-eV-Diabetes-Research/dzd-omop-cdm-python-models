import contextlib
import pg8000.native
from pathlib import Path, PurePath
from OMOPSQLModelGen.config import Config
from OMOPSQLModelGen.sources import OMOPSchemaSource

config = Config()


class ReferencePostgresHandler:
    def __init__(
        self,
        db_host: str,
        db_name: str,
        db_user: str,
        db_password: str,
        db_port: int = 5432,
        db_schema: str = "public",
    ):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.db_schema = db_schema

    @contextlib.contextmanager
    def db_con(self):
        """
        Create a DB connection
        """
        """HINT/NOTE: pg8000.native.Connection possible/default params
        user,
        host="localhost",
        database=None,
        port=5432,
        password=None,
        source_address=None,
        unix_sock=None,
        ssl_context=None,
        timeout=None,
        tcp_keepalive=True,
        application_name=None,
        replication=None,
        sock=None,
        """
        con = pg8000.native.Connection(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            port=self.db_port,
        )
        try:
            yield con
        finally:
            con.close()

    def run_sql_script_file(self, file_path: Path, schema_replace_str: str = None):
        with self.db_con() as db_con:
            with open(file_path) as sql_script:
                db_con.run(
                    sql_script.read().replace(
                        config.OMOP_SQL_SCRIPT_SCHEMA_PLACEHOLDER_STRING, self.db_schema
                    )
                )

    def wipe_schema_clean(self):
        """WARNING: This deletes all tables in the schema"""
        with self.db_con() as db:
            db.run(f"drop schema {self.db_schema} CASCADE;")

            db.run(f"create schema {self.db_schema};")

    def create_omop_schema(
        self, omop_schema_source: OMOPSchemaSource, wipe_clean_before: bool = False
    ):
        if wipe_clean_before is True:
            self.wipe_schema_clean()
        for sql_source_file in [
            omop_schema_source.sql_ddl_file_path,
            omop_schema_source.sql_primary_keys_file_path,
            omop_schema_source.sql_indices_file_path,
            omop_schema_source.sql_constraints_file_path,
        ]:

            sql_source_file_path = Path(
                PurePath(
                    config.OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR,
                    sql_source_file,
                )
            )
            self.run_sql_script_file(sql_source_file_path)
