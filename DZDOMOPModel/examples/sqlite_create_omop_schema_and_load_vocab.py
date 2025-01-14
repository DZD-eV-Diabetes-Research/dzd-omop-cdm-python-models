from sqlalchemy import create_engine
from omopmodel import OMOP_5_4_declarative as omop54
from omopmodel import VocabulariesLoader

# Define the connection to our sqlite database.
# if it does not exists, it will created on the fly
engine = create_engine("sqlite:///cdm_source.db", echo=False)

# Define the directory where our athena vocabularies csv files are stored.
authena_export_directory = "/home/tim/Downloads/tmp/athenalars"

# Create the OMOP Schema on our database
omop54.Base.metadata.create_all(engine)

# Initialize the vocabulary loader.
v = VocabulariesLoader(
    authena_export_directory,
    database_engine=engine,
    omop_module=omop54,  # <- This is optional. default is OMOP CDM V5.4
)
# Load the vocabulary from the CSV files into the database.
# HINT: If you are using a sqlite database this can take unbearably long
# sqlite is for testing and tinkering but will have a hard time storing larger vocabulary exports
# Use postgresql instead
v.load_all()
