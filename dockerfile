FROM python:3.12
COPY reqs_gen.txt /tmp/reqs_gen.txt
RUN python -m pip install -U -r /tmp/reqs_gen.txt
RUN mkdir /OMOPSQLModelGen
COPY OMOPSQLModelGen /OMOPSQLModelGen
WORKDIR /OMOPSQLModelGen
RUN mkdir -p /output
ENV DATAMODEL_OUTPUT_DIR=/output
RUN chmod 777 /output
RUN mkdir -p /input
RUN chmod 777 /input
ENV OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR=/input
ENTRYPOINT  [ "python", "main.py" ]