from sqlalchemy import create_engine
from omopmodel import OMOP_5_4_declarative as omop54
from omopmodel import VocabulariesLoader

# Define the connection to our running postgresql database
engine = create_engine("postgresql+pg8000://ps:ps@localhost/ps")

# Define the directory where our athena vocabularies csv files are stored.
authena_export_directory = "/home/me/Downloads/AthenaUnzipped"

# Create the OMOP Schema on our database
omop54.Base.metadata.create_all(engine)

# Initialize the vocabulary loader.
v = VocabulariesLoader(
    authena_export_directory,
    database_engine=engine,
    omop_module=omop54,  # <- This is optional. default is OMOP CDM V5.4
)
# Load the vocaablary from the CSV files into the database.
# This will take some time, you will see some progress bars.
# Take your time make a coffe
v.load_all()
