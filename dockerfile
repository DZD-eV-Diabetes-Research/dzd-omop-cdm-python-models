FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
ENV UV_PROJECT_ENVIRONMENT=/venv UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# Install the generator's locked dependencies only (no workspace packages)
WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY packages/dzdomop/pyproject.toml packages/dzdomop/pyproject.toml
COPY generator/pyproject.toml generator/pyproject.toml
RUN uv sync --locked --no-dev --package omop-codegen --no-install-workspace
ENV PATH=/venv/bin:$PATH
RUN mkdir /OMOPSQLModelGen
COPY generator/OMOPSQLModelGen /OMOPSQLModelGen
COPY LICENSE /OMOPSQLModelGen/LICENSE
WORKDIR /OMOPSQLModelGen
RUN mkdir -p /output
ENV DATAMODEL_OUTPUT_DIR=/output
RUN chmod 777 /output
RUN mkdir -p /input
RUN chmod 777 /input
ENV OMOP_CDM_RELEASE_DOWNLOAD_TARGET_DIR=/input
ENTRYPOINT  [ "python", "main.py" ]
