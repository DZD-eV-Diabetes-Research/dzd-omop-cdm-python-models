from typing import Type, List, Annotated, Dict, Callable, Optional
from types import FrameType, ModuleType, TracebackType
from pathlib import Path
import csv
from sqlalchemy import (
    Engine,
    text,
    URL,
    Column,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    Index,
    MetaData,
    Table,
)
from sqlalchemy.schema import AddConstraint, CreateIndex, DropConstraint, DropIndex
import sqlalchemy.inspection
from sqlalchemy.orm import Session
import datetime
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import ColumnProperty
from tqdm import tqdm

import inspect
from io import StringIO
import pg8000.native
import sqlite3
import traceback

# import sqlalchemy.inspection

if __name__ == "__main__":
    from pathlib import Path
    import sys, os

    MODULE_DIR = Path(__file__).parent
    MODULE_PARENT_DIR = MODULE_DIR.parent.absolute()
    sys.path.insert(0, os.path.normpath(MODULE_PARENT_DIR))

from omopmodel import OMOP_5_4_declarative
from omopmodel.OMOP_5_4_declarative import Base, Concept


class VocabularyLoader:

    def __init__(
        self,
        vocabulary_directory: Path | str,
        database_engine: Engine,
        flush_interval: Annotated[
            int,
            "Commit the so far parsed rows to the database and remove them from memory.",
        ] = 12000,
        drop_constraints_and_indexes_before_insert: Annotated[
            bool,
            "Before doing any insert statements, we try to disable foreign keys in the database. This can help with unresolvable fk cycles which are baked into OMOP atm https://github.com/OHDSI/CommonDataModel/issues/706",
        ] = True,
        recreate_constraints_and_indexes_after_insert: Annotated[
            bool,
            "If 'disable_foreign_keys_before_insert' was set to true, we can re-enable foreign keys after vocabulary loading.",
        ] = True,
        truncate_vocabulary_tables_before_insert: Annotated[
            bool,
            "Before doing any insert statements we will delete all rows in the current omop vocabulary table.",
        ] = False,
        show_progress_bar: bool = True,
        omop_module: ModuleType = OMOP_5_4_declarative,
        max_rows_pers_csv: Annotated[
            Optional[int],
            "When set only this amount of rows per csv/table will be parsed and inserted. This can be helpfull for debuging or a quick test run.",
        ] = None,
    ):
        if database_engine.driver not in ["pg8000", "pysqlite"]:
            raise ValueError(
                f"""At the moment only the pg8000 (postgresql) and pysqlite (sqlite) database driver is supported. Got {database_engine.driver}. """
                + """Please use https://pypi.org/project/pg8000/ or sqlite for your connection. e.g. `sqlalchemy.create_engine("postgresql+pg8000://user:password@localhost/mydb")` or `sqlalchemy.create_engine("sqlite:///./mydatadir/mydb.db")`"""
            )
        self.csv_date_format = "%Y%m%d"
        self.date_target_format = "%Y-%m-%d"
        if not isinstance(vocabulary_directory, Path):
            vocabulary_directory = Path(vocabulary_directory)
        self.vocabulary_directory = vocabulary_directory
        self.flush_interval = flush_interval
        self.database_engine = database_engine

        self.show_progress_bar = show_progress_bar
        self.drop_constraints_and_indexes_before_insert = (
            drop_constraints_and_indexes_before_insert
        )
        self.recreate_constraints_and_indexes_after_insert = (
            recreate_constraints_and_indexes_after_insert
        )
        self.truncate_vocabulary_tables = truncate_vocabulary_tables_before_insert
        self.origin_foreign_key_constrains_state: Optional[bool] = None
        self.omop_module = omop_module
        self.max_rows_pers_csv = max_rows_pers_csv
        self.csv_file_table_mapping: Dict[str, str] = {"CONCEPT_CPT4": None}

    def load_all(self):
        try:
            if self.drop_constraints_and_indexes_before_insert:
                self.drop_constraints_and_pks_and_indexes()
            for file_obj in self.vocabulary_directory.iterdir():
                if file_obj.is_file() and file_obj.suffix.lower() == ".csv":
                    tablename = self.csv_file_table_mapping.get(
                        file_obj.stem, file_obj.stem.lower()
                    )
                    omop_class: Optional[Base] = self._find_omop_class_by_tablename(
                        tablename
                    )
                    if omop_class is None:
                        print(
                            f"WARNING: Can not determine OMOP table for csv file '{file_obj}'. You can extent '{self.__class__.__name__}.csv_file_table_mapping' for manual csv file name to OMOP table mapping."
                        )
                        continue
                    self.load_csv(
                        omop_class,
                        file_obj,
                    )
        except (Exception, KeyboardInterrupt) as e:
            if self.recreate_constraints_and_indexes_after_insert:
                self.recreate_constraints_and_pks_and_indexes()
            if isinstance(e, Exception):
                raise e
            else:
                # traceback.print_exception(e)
                print("KeyboardInterrupt")
                exit(1)

        # end
        if self.recreate_constraints_and_indexes_after_insert:
            self.recreate_constraints_and_pks_and_indexes()

    def load_csv(self, omop_class: Type[Base], source_csv: Path):
        omop_class_attr_types: Dict[str, Callable] = self._get_class_attr_types(
            omop_class
        )
        if self.truncate_vocabulary_tables:
            self._truncate_table(omop_class.__tablename__)

        with open(source_csv, mode="r") as file:
            if self.show_progress_bar:
                row_count = self._count_csv_rows(source_csv) - 1
                progress_bar = tqdm(total=row_count, desc=source_csv.name)

            csv_reader = csv.reader(file, delimiter="\t")
            csv_headers: List[str]
            rows: List[List[str]] = []
            # Iterate over each row in the CSV file
            for row_no, row_raw in enumerate(csv_reader):

                if row_no == 0:
                    csv_headers = row_raw
                    continue

                for column_index, column_header in enumerate(csv_headers):
                    casting_function = omop_class_attr_types[column_header]
                    if casting_function == datetime.date:
                        row_raw[column_index] = datetime.datetime.strptime(
                            row_raw[column_index].strip(),
                            self.csv_date_format,
                        ).strftime(self.date_target_format)

                rows.append(row_raw)
                if len(rows) == self.flush_interval:
                    self._commit_rows(
                        rows=rows, omop_class=omop_class, column_order=csv_headers
                    )
                    rows = []
                if self.max_rows_pers_csv == row_no:
                    break
                if self.show_progress_bar:
                    progress_bar.update(1)
        if rows:
            # commit left over parsed and cached/non-commited rows
            self._commit_rows(
                rows=rows, omop_class=omop_class, column_order=csv_headers
            )
        if self.show_progress_bar:
            progress_bar.close()

        # Add your processing logic here

    def _get_class_attr_types(self, omop_class: Base) -> Dict[str, type]:
        # Get the class mapper to inspect the mapped properties
        mapper = class_mapper(omop_class)

        properties = {}
        for prop in mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                column = prop.columns[0]
                properties[prop.key] = column.type.python_type

        return properties

    def _find_omop_class_by_tablename(self, name: str) -> Optional[Type[Base]]:
        for omop_table_class in self._get_omop_orm_classes():
            if name == omop_table_class.__tablename__:
                return omop_table_class

    def _commit_rows(
        self,
        rows: List[List[str]],
        omop_class: Type[Base],
        column_order: Optional[List[str]] = None,
    ):
        if column_order is None:
            column_order = tuple(
                self._get_class_attr_types(omop_class=omop_class).keys()
            )
        if self.database_engine.driver == "pysqlite":
            self._commit_objs_with_sqlite_insert(rows, omop_class, column_order)
        elif self.database_engine.driver == "pg8000":
            self._commit_objs_with_postgres_copy(rows, omop_class, column_order)

    def _commit_objs_with_postgres_copy(
        self,
        rows: List[str],
        omop_class: Type[Base],
        column_order: List[str],
    ):
        with Session(self.database_engine) as session:
            stream_in = StringIO()
            csv_writer = csv.writer(stream_in)
            for row in rows:
                csv_writer.writerow(row)
            stream_in.seek(0)
            con: pg8000.native.Connection = session.connection().connection
            # https://www.postgresql.org/docs/current/sql-copy.html
            # https://github.com/tlocke/pg8000?tab=readme-ov-file#copy-from-and-to-a-stream
            statement = f"""COPY {omop_class.__tablename__}{str(tuple(column_order)).replace("'","")} FROM STDIN WITH (FORMAT CSV)"""
            # print("statement", statement)
            con.run(
                statement,
                stream=stream_in,
            )
            session.commit()

    def _commit_objs_with_sqlite_insert(
        self,
        rows: List[str],
        omop_class: Type[Base],
        column_order: List[str] = None,
    ):

        with Session(self.database_engine) as session:
            con: sqlite3.Connection = session.connection(
                {"cached_statements": self.flush_interval}
            ).connection
            # "INSERT INTO t (col1, col2) VALUES (?, ?);
            con.executemany(
                f"""insert into {omop_class.__tablename__}{str(column_order).replace("'","")} values ({",".join("?" * len(column_order))})""",
                rows,
            )
            session.commit()

    def _count_csv_rows(self, file_path: Path) -> int:
        with open(file_path, "r", encoding="utf-8") as file:
            row_count = sum(1 for _ in file)
        return row_count

    def set_foreign_key_constraints(self, enable: bool = True):
        if self.database_engine.dialect.name == "postgresql":
            print(f"""\n{"ENABLE" if enable else "DISABLE"} Database constraints.""")

            for omop_table_class in self._get_omop_orm_classes():
                self._postgres_set_constraints(
                    table_name=omop_table_class.__tablename__, enable=enable
                )

    def _postgres_set_constraints(self, table_name, enable: bool = None):
        key_word = "ENABLE" if enable else "DISABLE"
        statement = text(f"ALTER TABLE {table_name} {key_word} TRIGGER ALL;")
        with self.database_engine.connect() as conn:
            conn.execute(statement=statement)
            conn.commit()

    def _truncate_table(self, table_name):
        """
        Truncate a table in the database. Works with both SQLite and PostgreSQL.
        """
        print(f"TRUNCATE table {table_name}")
        if self.database_engine.dialect.name == "postgresql":
            truncate_sql = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
        elif self.database_engine.dialect.name == "sqlite":
            truncate_sql = f"DELETE FROM {table_name};"
        else:
            raise NotImplementedError(
                f"Truncate operation is not supported for dialect: {self.engine.dialect.name}"
            )

        # Execute the truncate statement
        with engine.connect() as connection:
            connection.execute(text(truncate_sql))
            connection.commit()

    def _get_omop_orm_classes(self) -> List[Type[Base]]:
        omop_classes = []
        for omop_table_class_name, omop_table_class in inspect.getmembers(
            self.omop_module, inspect.isclass
        ):
            if omop_table_class_name == "Base":
                base_class = omop_table_class
                continue
            elif not issubclass(omop_table_class, base_class):
                continue
            omop_classes.append(omop_table_class)
        return omop_classes

    def drop_constraints_and_pks_and_indexes(self):
        # DROP INDEXES
        with Session(self.database_engine) as session:
            for omop_table_class in self._get_omop_orm_classes():
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, Index):
                        session.execute(DropIndex(table_arg, if_exists=True))
            session.commit()
        # DROP FKs
        with Session(self.database_engine) as session:
            for omop_table_class in self._get_omop_orm_classes():
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, ForeignKeyConstraint):
                        session.execute(
                            DropConstraint(table_arg, if_exists=True, cascade=True)
                        )
            session.commit()
        # DROP PKs
        with Session(self.database_engine) as session:
            for omop_table_class in self._get_omop_orm_classes():
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, PrimaryKeyConstraint):

                        session.execute(
                            DropConstraint(table_arg, if_exists=True, cascade=True)
                        )

            session.commit()
        print("All foreign keys, primary keys, and indexes have been dropped.")

    def recreate_constraints_and_pks_and_indexes(self):
        with Session(self.database_engine) as session:
            for omop_table_class in self._get_omop_orm_classes():
                # create pks
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, PrimaryKeyConstraint):
                        session.execute(AddConstraint(table_arg))
                # create indexes
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, Index):
                        table_arg.create
                        session.execute(CreateIndex(table_arg, if_not_exists=True))
            session.commit()
        with Session(self.database_engine) as session:
            for omop_table_class in self._get_omop_orm_classes():
                # create fks
                for table_arg in omop_table_class.__table_args__:
                    if isinstance(table_arg, ForeignKeyConstraint):
                        session.execute(AddConstraint(table_arg))
            session.commit()


## local dev testing /home/tim/Downloads/AthenaVocab_DZD1.0/
p = Path("/home/tim/Downloads/AthenaVocab_DZD1.0/")


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_4_declarative as omop

# Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)
# engine = create_engine("sqlite:///cdm_source.db", echo=False)
engine = create_engine("postgresql+pg8000://ps:ps@localhost/ps")

omop.Base.metadata.create_all(engine)

v = VocabularyLoader(
    p,
    database_engine=engine,
    truncate_vocabulary_tables_before_insert=True,
    # max_rows_pers_csv=1000,
    recreate_constraints_and_indexes_after_insert=False,
)
v.load_all()
print("DOONE. recreate stuff")
# v.recreate_constraints_and_pks_and_indexes()
# todo: skip loaded csv (len(csv_rows) == len(rows in database))
