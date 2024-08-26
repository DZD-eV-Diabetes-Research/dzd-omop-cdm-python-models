from typing import Type, List, Annotated, Dict, Callable, Optional
from types import FrameType, ModuleType, TracebackType
from pathlib import Path
import csv
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session
import datetime
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import ColumnProperty
from tqdm import tqdm
import inspect

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
        ] = 1000,
        do_upserts: Annotated[
            bool,
            "Check if object exists before insert and update it instead of insert. This will have massive impact on perfomance, but you dont need to wipe your database befor running VocabularyLoader. Also have a look at `truncate_vocabulary_tables_before_insert` as an alternative.",
        ] = False,
        disable_foreign_keys_before_insert: Annotated[
            bool,
            "Before doing any insert statements, we try to disable foreign keys in the database. This can help with unresolvable fk cycles which are baked into OMOP atm https://github.com/OHDSI/CommonDataModel/issues/706",
        ] = False,
        truncate_vocabulary_tables_before_insert: Annotated[
            bool,
            "Before doing any insert statements we will delete all rows in the current omop vocabulary table.",
        ] = False,
        show_progress_bar: bool = True,
        omop_module: ModuleType = OMOP_5_4_declarative,
    ):
        self.csv_date_format = "%Y%m%d"
        if not isinstance(vocabulary_directory, Path):
            vocabulary_directory = Path(vocabulary_directory)
        self.vocabulary_directory = vocabulary_directory
        self.flush_interval = flush_interval
        self.database_engine = database_engine
        self.do_upserts = do_upserts
        self.show_progress_bar = show_progress_bar
        self.disable_foreign_keys = disable_foreign_keys_before_insert
        self.truncate_vocabulary_tables = truncate_vocabulary_tables_before_insert
        self.origin_foreign_key_constrains_state: Optional[bool] = None
        self.omop_module = omop_module

    def load_all(self):
        if self.disable_foreign_keys:
            self.set_foreign_key_constraints(False)
        # do stuff
        self.load_csv(
            Concept, Path("/home/tim/Downloads/AthenaVocab_DZD1.0/CONCEPT.csv")
        )

        # end
        self.set_foreign_key_constraints(True)

    def load_csv(self, omop_class: Type[Base], source_csv: Path):
        omop_objects: List[Base] = []
        omop_class_attr_types: Dict[str, Callable] = self.get_class_attr_types(
            omop_class
        )
        if self.truncate_vocabulary_tables:
            self._truncate_table(omop_class.__tablename__)

        with open(source_csv, mode="r") as file:
            if self.show_progress_bar:
                row_count = self._count_csv_rows(source_csv) - 1
                progress_bar = tqdm(total=row_count, desc=source_csv.name)

            csv_reader = csv.reader(file, delimiter="\t")
            headers: List[str]
            # Iterate over each row in the CSV file
            for row_no, row in enumerate(csv_reader):
                if row_no == 0:
                    headers = row
                    continue
                omop_object_data = {}
                for column_index, column_header in enumerate(headers):
                    row_cell_value_raw: str = row[column_index]
                    casting_function = omop_class_attr_types[column_header]
                    if row_cell_value_raw == "":
                        row_cell_value_casted = None
                    if casting_function == datetime.date:
                        row_cell_value_casted = datetime.datetime.strptime(
                            row_cell_value_raw.strip(), "%Y%m%d"
                        )
                    else:
                        row_cell_value_casted = casting_function(row_cell_value_raw)
                    omop_object_data[column_header] = row_cell_value_casted
                omop_object = omop_class(**omop_object_data)
                omop_objects.append(omop_object)
                if len(omop_objects) == self.flush_interval:
                    self._commit_objs(omop_objs=omop_objects)
                    omop_objects = []

                # if row_no > 10000:
                #    break
                if self.show_progress_bar:
                    progress_bar.update(1)
        if omop_objects:
            # commit left over parsed and cached/non-commited omop obj
            self._commit_objs(omop_objs=omop_objects)
        if self.show_progress_bar:
            progress_bar.close()

        # Add your processing logic here

    def get_class_attr_types(self, omop_class: Base) -> Dict[str, type]:
        # Get the class mapper to inspect the mapped properties
        mapper = class_mapper(omop_class)

        properties = {}
        for prop in mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                column = prop.columns[0]
                properties[prop.key] = column.type.python_type

        return properties

    def _commit_objs(self, omop_objs: List[Base]):
        with Session(self.database_engine) as session:
            if self.do_upserts:
                for obj in omop_objs:
                    session.merge(obj)
            else:
                session.add_all(omop_objs)
            session.commit()

    def _count_csv_rows(self, file_path: Path) -> int:
        with open(file_path, "r", encoding="utf-8") as file:
            row_count = sum(1 for _ in file)
        return row_count

    def set_foreign_key_constraints(self, enable: bool = True):
        if self.database_engine.dialect.name == "postgresql":
            for omop_table_class in inspect.getmembers(
                self.omop_module, inspect.isclass
            ):
                if omop_table_class[0] == "Base":
                    base_class = omop_table_class[1]
                    continue
                if issubclass(omop_table_class[1], base_class):
                    self._postgres_set_constraints(
                        table_name=omop_table_class[1].__tablename__, enable=enable
                    )

    def _postgres_set_constraints(self, table_name, enable: bool = None):
        key_word = "ENABLE" if enable else "DISABLE"
        statement = text(f"ALTER TABLE {table_name} {key_word} TRIGGER ALL;")
        with self.database_engine.connect() as conn:
            print("RUN", statement)
            conn.execute(statement=statement)
            conn.commit()

    def _truncate_table(self, table_name):
        """
        Truncate a table in the database. Works with both SQLite and PostgreSQL.
        """

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


TODO:
# Have a look at COPY https://github.com/tlocke/pg8000?tab=readme-ov-file#copy-from-and-to-a-stream

## local dev testing /home/tim/Downloads/AthenaVocab_DZD1.0/
p = Path("/home/tim/Downloads/AthenaVocab_DZD1.0/CONCEPT.csv")


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from omopmodel import OMOP_5_3_declarative as omop

# Create a SQLite database and deploy the omop schema (tables,constraints, indices and primary keys)
# engine = create_engine("sqlite:///cdm_source.db", echo=False)
engine = create_engine("postgresql+pg8000://ps:ps@localhost/ps")
omop.Base.metadata.create_all(engine)

v = VocabularyLoader(
    p,
    database_engine=engine,
    flush_interval=1000,
    do_upserts=False,
    disable_foreign_keys_before_insert=True,
    truncate_vocabulary_tables_before_insert=True,
)

v.load_all()
