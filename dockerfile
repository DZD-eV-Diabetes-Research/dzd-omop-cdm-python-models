FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
ENV UV_PROJECT_ENVIRONMENT=/venv UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /workspace
# Locked dependencies first (cached layer), then the generator itself
COPY pyproject.toml uv.lock ./
COPY packages/dzdomop/pyproject.toml packages/dzdomop/pyproject.toml
COPY generator/pyproject.toml generator/pyproject.toml
RUN uv sync --locked --no-dev --package omop-codegen --no-install-workspace
COPY generator/src generator/src
RUN uv sync --locked --no-dev --package omop-codegen --no-editable
ENV PATH=/venv/bin:$PATH
RUN mkdir -p /output /downloads && chmod 777 /output /downloads
ENV DATAMODEL_OUTPUT_DIR=/output OMOP_CDM_DOWNLOAD_DIR=/downloads
WORKDIR /output
ENTRYPOINT ["omop-codegen"]
