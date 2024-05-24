from typing import List, Dict
import contextlib
import pg8000.native
from pathlib import Path, PurePath
from OMOPSQLModelGen.config import Config
from OMOPSQLModelGen.sources import OMOPSchemaSource
import csv
import json

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
            self.run_sql_script_file(sql_source_file)

    def enrich_omop_schema_metadata(self, omop_schema_source: OMOPSchemaSource):
        """Add comments to tables and field based on the OMOP Documentation (csv files)

        Args:
            omop_schema_source (OMOPSchemaSource): _description_
        """
        all_table_names_query = f"SELECT table_name FROM information_schema.tables  WHERE table_schema = '{self.db_schema}'"

        with self.db_con() as db:
            all_table_names = [tbl[0] for tbl in db.run(all_table_names_query)]
        table_metadata = self._get_table_metadata(omop_schema_source=omop_schema_source)
        all_field_metadata = self._get_field_metadata(
            omop_schema_source=omop_schema_source
        )
        sql_statements: List[str] = []
        for table_name in all_table_names:
            table_name: str = table_name.upper()
            table_comment = f"""DESC: {table_metadata[table_name]["tableDescription"]} \nUSER GUIDANCE: {table_metadata[table_name]["userGuidance"]} \nETLCONVENTIONS: {table_metadata[table_name]["etlConventions"]}""".replace(
                "'", '"'
            )
            create_table_comment_statement = (
                f"COMMENT ON TABLE {self.db_schema}.{table_name} IS '{table_comment}';"
            )
            sql_statements.append(create_table_comment_statement)
            all_column_names_query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{self.db_schema}' AND upper(table_name)   = '{table_name}';"
            with self.db_con() as db:
                all_col_names = [tbl[0] for tbl in db.run(all_column_names_query)]
            field_metadata_for_table = all_field_metadata[table_name]
            for field_name in all_col_names:
                print("table", table_name)
                field_metadata = field_metadata_for_table[field_name]
                print("field_metadata", field_metadata)
                field_comment = f"""USER GUIDANCE: {field_metadata["userGuidance"]} \nETLCONVENTIONS: {field_metadata["etlConventions"]}""".replace(
                    "'", '"'
                )
                add_field_comment_sql_statement = f"COMMENT ON COLUMN {self.db_schema}.{table_name}.{field_name} IS '{field_comment}';"
                sql_statements.append(add_field_comment_sql_statement)
        with self.db_con() as db:
            db.run("\n".join(sql_statements))

    def _get_table_metadata(self, omop_schema_source: OMOPSchemaSource):
        # todo: IMPROVE THIS! It is unreadable...
        metadata: Dict[str, Dict[str, str]] = {}
        with open(omop_schema_source.csv_table_desc_file_path, "r") as file:
            csv_rows: List = list(csv.reader(file, delimiter=","))
            header_row = csv_rows.pop(0)
            for row in csv_rows:
                table_data = {}
                metadata[row[0]] = table_data
                for col_index, cell in enumerate(row):
                    table_data[header_row[col_index]] = cell
        return metadata

    def _get_field_metadata(self, omop_schema_source: OMOPSchemaSource):
        # todo: IMPROVE THIS! It is unreadable...
        metadata: Dict[str, Dict[str, Dict[str, str]]] = {}
        with open(omop_schema_source.csv_field_desc_file_path, "r") as file:
            csv_rows: List = list(csv.reader(file, delimiter=","))
            header_row = csv_rows.pop(0)
            for row in csv_rows:
                table_name = row[0]
                field_name = row[1].replace('"', "")
                field_data = {"name": field_name}
                for col_index, cell in enumerate(row):
                    field_data[header_row[col_index]] = cell
                if table_name not in metadata:
                    metadata[table_name] = {}
                metadata[table_name][field_name] = field_data
        return metadata
