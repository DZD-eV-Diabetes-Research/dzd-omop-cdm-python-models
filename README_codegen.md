# Code Generator for OMOP Schema

## How it works


All the code for the OMOP Data Class Generator can be found in [`OMOPSQLModelGen`](OMOPSQLModelGen) in this repo

The Code Generator does following steps:

* Download OMOP Schema releases from github https://github.com/OHDSI/CommonDataModel/releases according to [`OMOPSQLModelGen/sources.py`](OMOPSQLModelGen/sources.py)
* Deploy the SQL Schema to a running PostgresSQL Database
* Do some adjustments to the schema as defined in [`OMOPSQLModelGen/pre_gen_sql`](OMOPSQLModelGen/pre_gen_sql) (e.g. Add temporary Primary Keys for example to be compatible with SQLAlchemy ORM)
* Run [sqlacodegen](https://github.com/agronholm/sqlacodegen) against the Postgres Database to generate python data classes
* Run some adjustments on the generated code as defined in [`OMOPSQLModelGen/post_processing_funcs`](OMOPSQLModelGen/post_processing_funcs)

## How can you run it

### With docker

requirements:
* Linux environment
* [Docker](https://docs.docker.com/get-started/get-docker/) (with [`docker compose`](https://docs.docker.com/compose/install/))

just run [`run_codegen.sh`](run_codegen.sh) or have a look what it does.
In a nutshell it does the following which you also run by yourself:

`docker compose build`
`docker compose up -d`
`docker compose logs -f omopcodegen`
`docker compose down`