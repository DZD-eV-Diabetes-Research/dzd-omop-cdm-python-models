"""``omop-codegen``: generate the OMOP model modules.

Settings come from env vars or ``.env`` (see ``config.py``). The command line overrides
the most common ones.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import tempfile
from pathlib import Path

from omop_codegen.cdm_versions import CDM_VERSIONS
from omop_codegen.config import FLAVORS, Settings
from omop_codegen.database import deploy_ddl, make_engine, reflect
from omop_codegen.download import fetch_release
from omop_codegen.enrich import add_comments, mark_candidate_keys
from omop_codegen.generate import render
from omop_codegen.omop_policy import CANDIDATE_KEYS

log = logging.getLogger("omop_codegen")


def run(settings: Settings) -> list[Path]:
    """Generate every configured version × flavor. Returns the written files."""
    unknown = set(settings.CDM_VERSIONS) - CDM_VERSIONS.keys()
    if unknown:
        raise ValueError(f"Unknown CDM versions {sorted(unknown)}, known: {sorted(CDM_VERSIONS)}")

    release_dir = fetch_release(
        settings.OMOP_CDM_RELEASE_TAG,
        settings.OMOP_CDM_DOWNLOAD_DIR,
        force=settings.FORCE_REDOWNLOAD_OMOP_CDM_RELEASE,
    )
    engine = make_engine(settings.sql_url(), settings.POSTGRESQL_SCHEMA)
    output_dir = settings.DATAMODEL_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Everything goes to a staging dir first. Only a complete run replaces files in output_dir.
    staging = Path(tempfile.mkdtemp(prefix=".omop-codegen-", dir=output_dir))
    try:
        for name in settings.CDM_VERSIONS:
            version = CDM_VERSIONS[name]
            deploy_ddl(engine, settings.POSTGRESQL_SCHEMA, version.ddl_files(release_dir))
            for flavor in settings.FLAVORS:
                module = f"{version.module_prefix}_{flavor}"
                log.info("Generating %s", module)
                # sqlacodegen changes the MetaData it renders, so every flavor gets a fresh one.
                metadata = reflect(engine)
                add_comments(
                    metadata, version.table_csv(release_dir), version.field_csv(release_dir)
                )
                mark_candidate_keys(metadata, CANDIDATE_KEYS[name])
                source = render(
                    metadata,
                    engine,
                    flavor,
                    cdm_version=name,
                    release_tag=settings.OMOP_CDM_RELEASE_TAG,
                )
                compile(source, f"{module}.py", "exec")  # fail here, not when users import it
                (staging / f"{module}.py").write_text(source, encoding="utf-8")

        written = []
        for path in sorted(staging.iterdir()):
            target = output_dir / path.name
            os.replace(path, target)
            written.append(target)
            log.info("Wrote %s", target)
        return written
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        engine.dispose()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="omop-codegen", description=__doc__)
    parser.add_argument("-o", "--output", type=Path, help="output dir (DATAMODEL_OUTPUT_DIR)")
    parser.add_argument(
        "--cdm-version",
        action="append",
        choices=sorted(CDM_VERSIONS),
        help="repeatable (CDM_VERSIONS)",
    )
    parser.add_argument("--flavor", action="append", choices=FLAVORS, help="repeatable (FLAVORS)")
    args = parser.parse_args(argv)

    overrides = {
        "DATAMODEL_OUTPUT_DIR": args.output,
        "CDM_VERSIONS": args.cdm_version,
        "FLAVORS": args.flavor,
    }
    settings = Settings(**{k: v for k, v in overrides.items() if v is not None})
    logging.basicConfig(
        level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.captureWarnings(True)  # e.g. SQLAlchemy's FK cycle warning for concept <-> vocabulary
    log.info(
        "Database: %s, schema %s", settings.sql_url().render_as_string(), settings.POSTGRESQL_SCHEMA
    )
    run(settings)
