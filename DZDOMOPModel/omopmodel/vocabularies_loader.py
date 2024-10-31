from typing import Type, List, Annotated, Dict, Callable, Optional
from typing_extensions import Self
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
from sqlalchemy.schema import (
    AddConstraint,
    CreateIndex,
    DropConstraint,
    DropIndex,
    DropTable,
    CreateTable,
)
import itertools
import sqlalchemy.inspection
from sqlalchemy.orm import Session
import datetime
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import ColumnProperty

import sqlmodel
import inspect
from io import StringIO
import pg8000.native
import sqlite3
import dataclasses

# import sqlalchemy.inspection

if __name__ == "__main__":
    from pathlib import Path
    import sys, os

    MODULE_DIR = Path(__file__).parent
    MODULE_PARENT_DIR = MODULE_DIR.parent.absolute()
    sys.path.insert(0, os.path.normpath(MODULE_PARENT_DIR))

from omopmodel import OMOP_5_4_declarative
from omopmodel.OMOP_5_4_declarative import Base


@dataclasses.dataclass
class _CSVFileMetadataContainer:
    filepath: Path
    rows_no: int
    mapped_tablename: str
    mapped_omop_class: Optional[Base] = None

    @classmethod
    def from_path(
        cls: Type[Self],
        csv_path: Path,
        static_filename_table_mapping: Dict[str, str] = {},
    ) -> Self:
        line_count = None
        with open(csv_path, mode="r") as file:
            # -1 for headers
            line_count = sum(1 for row in file) - 1
            file.seek(0)
        table_name = static_filename_table_mapping.get(
            csv_path.stem, csv_path.stem.lower()
        )
        return cls(filepath=csv_path, rows_no=line_count, mapped_tablename=table_name)


class _VocabularyLoaderState(sqlmodel.SQLModel, table=True):
    __tablename__ = "_vocabulary_loader_state"
    filename: str = sqlmodel.Field(primary_key=True)
    file_total_rows: int = sqlmodel.Field(primary_key=True)
    target_tablename: str
    row_no_commited: Optional[int] = sqlmodel.Field(default=0)
    created_at: datetime.datetime = sqlmodel.Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )


class _VocabularyLoaderStateManager:
    def __init__(self, database_engine: Engine):
        self.database_engine = database_engine

    def create_loader_state_table(self, if_not_exists: bool = True):
        state_table: sqlalchemy.Table = _VocabularyLoaderState.__table__
        with sqlmodel.Session(self.database_engine) as session:
            session.exec(CreateTable(state_table, if_not_exists=if_not_exists))
            session.commit()

    def drop_loader_state_table(self, if_exists: bool = False):
        state_table: sqlalchemy.Table = _VocabularyLoaderState.__table__
        with sqlmodel.Session(self.database_engine) as session:
            session.exec(DropTable(state_table, if_exists=if_exists))
            session.commit()

    def get_or_create_loader_file_state(
        self, csv_file: _CSVFileMetadataContainer
    ) -> _VocabularyLoaderState:
        state: Optional[_VocabularyLoaderState] = None
        query = sqlmodel.select(_VocabularyLoaderState).where(
            _VocabularyLoaderState.filename == csv_file.filepath.name
            and _VocabularyLoaderState.file_total_rows == csv_file.rows_no
        )
        with sqlmodel.Session(self.database_engine) as session:
            state = session.exec(query).one_or_none()
        if state is None:
            state = _VocabularyLoaderState(
                filename=csv_file.filepath.name,
                file_total_rows=csv_file.rows_no,
                target_tablename=csv_file.mapped_tablename,
                row_no_commited=0,
            )
            state = self.save_loader_file_state(state)
        return state

    def save_loader_file_state(self, state: _VocabularyLoaderState):
        with Session(self.database_engine) as session:
            session.add(state)
            session.commit()
            session.refresh(state)

        return state

    def reset_state_for_table(self, tablename: str):
        query = sqlmodel.select(_VocabularyLoaderState).where(
            _VocabularyLoaderState.target_tablename == tablename
        )
        with sqlmodel.Session(self.database_engine) as session:
            result = session.exec(query)
            for state in result:
                state.row_no_commited = 0
                session.add(state)
            session.commit()


class VocabulariesLoader:

    def __init__(
        self,
        vocabulary_directory: Path | str,
        database_engine: Engine,
        flush_interval: Annotated[
            int,
            "Commit the so far parsed rows to the database and remove them from memory.",
        ] = 20000,
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
        save_loader_state_into_table: Annotated[
            bool,
            "If set to True we will create an extra table that save the state of loading into an extra table. That will enable continueing canceled vocabulary loading runs.",
        ] = True,
    ):
        """Load athena exported vocabulary into an existing OMOP CDM Schema. This will help you to speed things up by disabling constraints.
        Also this class can catch up on cancled load processes."""

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
        # Both CONCEPT_CPT4 and CONCEPT_ANCESTOR had corrupt data in my exports. Lets exlude them by default
        self.csv_file_table_mapping: Dict[str, str] = {
            "CONCEPT_CPT4": "concept",
        }
        self.allready_truncated_tables: List[str] = []
        self.save_loader_state_into_table = save_loader_state_into_table
        self.loader_state_manager: Optional[_VocabularyLoaderStateManager] = None
        self.initial_sqlite_fk_pragma: Optional[bool] = None
        # self._create_loader_state_table_if_not_exists()

    """
    def add_null_concept(self):
        '''Add a Concept with the ID 0 with fitting domain,vocabulary and conceptclass'''
        self.omop_module: OMOP_5_4_declarative = self.omop_module
        domain = self.omop_module.Domain()
        domain.domain_id = 0
        domain.domain_name = "NullClass"
        domain.domain_concept_id = 0

        vocabulary = self.omop_module.Vocabulary()
        vocabulary.vocabulary_id = 0
        vocabulary.vocabulary_name = "NullVocabulary"

        concept_class = self.omop_module.ConceptClass()
        concept_class.concept_class_id = 0
        concept_class.concept_class_name = "NullConceptClass"

        concept = self.omop_module.Concept()
        concept.concept_id = 0
        concept.concept_name = "No matching concept"
        concept.domain_id = 0
        concept.vocabulary_id = 0
        concept.concept_class_id = 0
        concept.concept_code = "No matching concept"
        concept.valid_start_date = datetime.date(year=1970, month=1, day=1)
        concept.valid_end_date = datetime.date(year=2099, month=12, day=31)
    """

    def load_all(self):
        """Try to load all CSVs in the given directory ('VocabularyLoader.vocabulary_directory')

        Raises:
            e: _description_
        """

        if self.save_loader_state_into_table:
            self.loader_state_manager = _VocabularyLoaderStateManager(
                database_engine=self.database_engine
            )
            self.loader_state_manager.create_loader_state_table(if_not_exists=True)
        try:
            if self.drop_constraints_and_indexes_before_insert:
                self.drop_constraints_and_pks_and_indexes()
            # if add_null_concept:
            #    print("Add null concept")
            #    self.add_null_concept()

            for file_obj in self.vocabulary_directory.iterdir():

                if file_obj.is_file() and file_obj.suffix.lower() == ".csv":
                    csv_container = self._determine_csv_file_mapping(file_obj)
                    if csv_container.mapped_omop_class is None:
                        print(
                            f"WARNING: Can not determine OMOP table for csv file '{file_obj}'. You can extent '{self.__class__.__name__}.csv_file_table_mapping' for manual 'csv file name' to 'OMOP table' mapping."
                        )
                        continue
                    self.load_csv(csv_container)

        except (Exception, KeyboardInterrupt) as e:
            if self.recreate_constraints_and_indexes_after_insert:

                self.recreate_constraints_and_pks_and_indexes()
            if isinstance(e, Exception):
                raise e
            else:
                # traceback.print_exception(e)
                print("KeyboardInterrupt")

        # end
        if self.recreate_constraints_and_indexes_after_insert:
            self.recreate_constraints_and_pks_and_indexes()

    # todo. make this interface more approchable by also accepting path and string
    def load_csv(
        self,
        source_csv: _CSVFileMetadataContainer | Path | str,
        omop_class: Optional[Base] = None,
    ):
        """Load a single csv into the database. We try to determine the correct table by the filename. If that is not possible you need to provide a OMOP CDM ORM Class at omop_class.

        Args:
            source_csv (_CSVFileMetadataContainer | Path | str): _description_
            omop_class (Optional[Base], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """
        # todo: this function is way to complex. need to break it down
        if isinstance(
            source_csv,
            (Path, str),
        ):
            source_csv = self._determine_csv_file_mapping(source_csv, omop_class)

        if source_csv.mapped_omop_class is None:
            raise ValueError(
                f"Can not determine OMOP ORM Class and target Table for csv file '{source_csv.filepath}'. Expected a OMOP CDM ORM class in param 'omop_class' at '{self.__class__.__name__}.load_csv()'. got {omop_class}"
            )

        omop_class_attr_types: Dict[str, Callable] = self._get_class_attr_types(
            source_csv.mapped_omop_class
        )
        if (
            self.truncate_vocabulary_tables
            and source_csv.mapped_tablename not in self.allready_truncated_tables
        ):
            # empty the whole vocabulary table
            self._truncate_table(source_csv.mapped_tablename)
            if self.loader_state_manager:
                self.loader_state_manager.reset_state_for_table(
                    source_csv.mapped_tablename
                )
            # we only want the table to be truncated once
            # because it is possible that we will load multiple csvs into the table
            # we dont want to wipe the previous loaded csv data
            self.allready_truncated_tables.append(source_csv.mapped_tablename)
        continue_at_row_no = 0
        if self.loader_state_manager:
            file_loading_process_state = (
                self.loader_state_manager.get_or_create_loader_file_state(source_csv)
            )

            continue_at_row_no = file_loading_process_state.row_no_commited + 1
        if continue_at_row_no > source_csv.rows_no:
            print(
                f"{source_csv.filepath.name} vocabulary source file seems to be loaded allready. Will skip..."
            )
            return
        with open(source_csv.filepath, mode="r") as file:
            # skip allready loaded lines

            csv_reader = csv.reader(file, delimiter="\t")
            csv_headers: List[str] = next(csv_reader)
            rows: List[List[str]] = []
            # Iterate over each row in the CSV file
            if self.show_progress_bar:
                from tqdm import tqdm

                progress_bar = tqdm(
                    total=source_csv.rows_no,
                    desc=source_csv.filepath.name,
                )
            skipped_lines_since_last_progressbar_update = 0
            for row_no, row_raw in enumerate(csv_reader):

                if row_no + 1 < continue_at_row_no:
                    # we pick up at an old state
                    # lets skip the allready loaded lines
                    if self.show_progress_bar:
                        skipped_lines_since_last_progressbar_update += 1
                        if (
                            skipped_lines_since_last_progressbar_update
                            > self.flush_interval
                        ):
                            progress_bar.update(
                                skipped_lines_since_last_progressbar_update
                            )
                            skipped_lines_since_last_progressbar_update = 0
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
                        rows=rows,
                        column_order=csv_headers,
                        source_csv=source_csv,
                    )
                    if self.show_progress_bar:
                        progress_bar.update(
                            (row_no - progress_bar.n)
                            + skipped_lines_since_last_progressbar_update
                        )
                        skipped_lines_since_last_progressbar_update = 0
                    rows = []

                if self.max_rows_pers_csv == row_no:
                    break

        if rows:
            # commit left over parsed and cached/non-commited rows
            self._commit_rows(
                rows=rows,
                column_order=csv_headers,
                source_csv=source_csv,
            )
            if self.show_progress_bar:
                progress_bar.update(
                    len(rows) + skipped_lines_since_last_progressbar_update
                )
        if self.show_progress_bar:
            progress_bar.close()

        # Add your processing logic here

    def _determine_csv_file_mapping(
        self, csv_path: Path, omop_class: Optional[Base] = None
    ) -> _CSVFileMetadataContainer:
        csv_container = _CSVFileMetadataContainer.from_path(csv_path)
        if omop_class:
            tablename = omop_class.__tablename__
        else:
            tablename = self.csv_file_table_mapping.get(
                csv_path.stem, csv_path.stem.lower()
            )
        if omop_class:
            csv_container.mapped_omop_class = omop_class
        else:
            csv_container.mapped_omop_class = self._find_omop_class_by_tablename(
                tablename
            )
        return csv_container

    def reset_state(self):
        """If 'VocabularyLoader.save_loader_state_into_table' is set to True, we keep track of allready loaded CSVs and rows to be able to continue on a e.g. canceled vocabulary loading process.
        If you want a fresh start you can reset the state with this function. This way we assume nothing is loaded yet.
        """
        loader_manager = self.loader_state_manager
        if self.loader_state_manager is None:
            loader_manager = _VocabularyLoaderStateManager(self.database_engine)
        loader_manager.drop_loader_state_table(if_exists=True)

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
        source_csv: _CSVFileMetadataContainer,
        column_order: Optional[List[str]] = None,
    ):
        if column_order is None:
            column_order = tuple(
                self._get_class_attr_types(
                    omop_class=source_csv.mapped_omop_class
                ).keys()
            )
        if self.database_engine.driver == "pysqlite":
            self._commit_objs_with_sqlite_insert(
                rows, source_csv.mapped_omop_class, column_order
            )
        elif self.database_engine.driver == "pg8000":
            self._commit_objs_with_postgres_copy(
                rows, source_csv.mapped_omop_class, column_order
            )
        self._save_commited_rows_state_if_needed(
            csv_file=source_csv, commited_rows=rows
        )

    def _save_commited_rows_state_if_needed(
        self,
        csv_file: _CSVFileMetadataContainer,
        commited_rows: List[List[str]],
    ):
        if self.loader_state_manager is not None:
            state = self.loader_state_manager.get_or_create_loader_file_state(csv_file)
            state.row_no_commited = state.row_no_commited + len(commited_rows)
            self.loader_state_manager.save_loader_file_state(state)

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
                f"""insert into {omop_class.__tablename__}{str(tuple(column_order)).replace("'","")} values ({",".join("?" * len(column_order))})""",
                rows,
            )
            session.commit()

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
        with self.database_engine.connect() as connection:
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
        if self.database_engine.driver in ["pg8000"]:
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
        elif self.database_engine.driver in ["pysqlite", "sqlite"]:
            # sqlite wont let us change any constrinas :(
            # https://sqlite.org/lang_altertable.html
            # the only thing we can do to speed things up a little bit is disable foreign key constraints
            with Session(self.database_engine) as session:
                print(
                    "INFO: You are trying disable database constraints to speed up, the vocabulary ingestion. But constrain disabling is not supported on sqlite. Try to use a postgresql database, if you need to speed up things."
                )
                initial_sqlite_fk_pragma_row = session.execute(
                    text("PRAGMA foreign_keys;")
                ).one_or_none()
                if initial_sqlite_fk_pragma_row is not None:
                    # if "None" we are on an old sqlite version with no support for this
                    self.initial_sqlite_fk_pragma = bool(
                        initial_sqlite_fk_pragma_row[0]
                    )
                    session.execute(text("PRAGMA foreign_keys = OFF;"))
                    session.commit()

    def recreate_constraints_and_pks_and_indexes(self):
        print(
            "INFO: Try to recreate constrains and rebuild indexes. This may take some time..."
        )
        if self.database_engine.driver in ["pg8000"]:
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
        elif self.database_engine.driver in ["pysqlite", "sqlite"]:
            # sqlite wont let us change any constrinas :(
            # https://sqlite.org/lang_altertable.html
            # the only thing we can do to speed things up a little bit is disable foreign key constraints
            with Session(self.database_engine) as session:
                current_pragma_row = session.execute(
                    text("PRAGMA foreign_keys;")
                ).one_or_none()
                if current_pragma_row is not None:
                    # if "None" we are on an old sqlite version with no support for this
                    session.execute(
                        text(
                            f"PRAGMA foreign_keys = {'ON' if self.initial_sqlite_fk_pragma else 'OFF'};"
                        )
                    )
                    session.commit()


"""
## local dev testing /home/tim/Downloads/AthenaVocab_DZD1.0/
p = Path("/home/tim/Downloads/AthenaVocab_DZDExportV1NoCPT4/")
# p = Path("/home/tim/Downloads/tmp/ll/")


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_4_declarative as omop

# Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)
# engine = create_engine("sqlite:///cdm_source.db", echo=False)
engine = create_engine("postgresql+pg8000://ps:ps@localhost/ps")

omop.Base.metadata.create_all(engine)

v = VocabulariesLoader(
    p,
    database_engine=engine,
    truncate_vocabulary_tables_before_insert=True,
    # max_rows_pers_csv=100,
    drop_constraints_and_indexes_before_insert=True,
    recreate_constraints_and_indexes_after_insert=True,
)
v.load_all()

print("DOONE. recreate stuff")
v.recreate_constraints_and_pks_and_indexes()
exit()
"""
