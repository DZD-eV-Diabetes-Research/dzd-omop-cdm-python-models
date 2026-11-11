"""``dzdomop load-vocab``: load an Athena export from the command line."""

from __future__ import annotations

import argparse
import importlib
import logging
import os
import sys
from collections.abc import Sequence

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from omopmodel.vocab.constraints import ConstraintRecreateError
from omopmodel.vocab.csv_source import CsvFormatError, VocabularySourceError
from omopmodel.vocab.download import DOWNLOAD_DIR_ENV, KEEP_DOWNLOAD_ENV
from omopmodel.vocab.loader import VocabulariesLoader, VocabularyLoaderError
from omopmodel.vocab.writers import UnsupportedDatabaseError

URL_ENV = "DZDOMOP_DATABASE_URL"
CDM_VERSIONS = ("5.3", "5.4", "5.5")
FLAVORS = ("declarative", "dataclasses", "sqlmodels", "tables")


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {number}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dzdomop", description="dzdomop command line tools")
    commands = parser.add_subparsers(dest="command", required=True)

    load = commands.add_parser(
        "load-vocab",
        help="load an Athena vocabulary export into an OMOP database",
        description="Load an Athena vocabulary export (https://athena.ohdsi.org) into an "
        "OMOP CDM database (PostgreSQL or SQLite).",
    )
    load.add_argument(
        "source",
        metavar="SOURCE",
        help="the Athena export: a folder with the CSV files, the zip file, or an http(s) "
        "URL to the zip (the download link from Athena's e-mail)",
    )
    load.add_argument(
        "--url",
        default=os.environ.get(URL_ENV),
        help=f"SQLAlchemy database URL, e.g. postgresql+psycopg://user:pw@host/db "
        f"or sqlite:///omop.db (default: ${URL_ENV})",
    )
    load.add_argument("--cdm-version", choices=CDM_VERSIONS, default="5.4")
    load.add_argument(
        "--flavor",
        choices=FLAVORS,
        default="declarative",
        help="model module whose keys and indexes are used (default: declarative)",
    )
    load.add_argument(
        "--create-tables",
        action="store_true",
        help="create the missing OMOP tables first (metadata.create_all)",
    )
    load.add_argument(
        "--truncate", action="store_true", help="empty each table before loading into it"
    )
    load.add_argument(
        "--keep-constraints",
        action="store_true",
        help="don't drop keys and indexes before loading (slower)",
    )
    load.add_argument(
        "--no-recreate",
        action="store_true",
        help="don't recreate keys and indexes after loading",
    )
    load.add_argument(
        "--no-state",
        action="store_true",
        help="don't track loaded rows (no resume after an interrupted run)",
    )
    load.add_argument(
        "--reset-state",
        action="store_true",
        help="forget earlier runs and load every file from the start",
    )
    load.add_argument(
        "--skip-invalid-foreign-keys",
        action="store_true",
        help="only warn about foreign keys that the data breaks (partial exports)",
    )
    load.add_argument("--flush-interval", type=_positive_int, default=20000, metavar="ROWS")
    load.add_argument(
        "--max-rows", type=_positive_int, metavar="ROWS", help="load at most ROWS per file"
    )
    load.add_argument(
        "--download-dir",
        metavar="DIR",
        help=f"URL source: folder for the downloaded zip (default: ${DOWNLOAD_DIR_ENV}, "
        "else 'dzdomop' in the system's temp folder)",
    )
    load.add_argument(
        "--keep-download",
        action="store_true",
        default=None,
        help="URL source: keep the zip after a successful load (default: "
        f"${KEEP_DOWNLOAD_ENV}, else delete it). After a failed load it is always kept.",
    )
    load.add_argument("--no-progress", action="store_true", help="no progress bars")
    load.add_argument("-q", "--quiet", action="store_true", help="only print warnings")
    return parser


def load_vocab(args: argparse.Namespace) -> None:
    if not args.url:
        raise SystemExit(f"error: no database URL. Pass --url or set ${URL_ENV}.")
    module_name = f"omopmodel.OMOP_{args.cdm_version.replace('.', '_')}_{args.flavor}"
    omop = importlib.import_module(module_name)
    engine = create_engine(args.url)
    log = logging.getLogger("omopmodel.vocab")
    log.info("Database %s, model %s", make_url(args.url).render_as_string(), module_name)

    if args.create_tables:
        omop.metadata.create_all(engine)
    loader = VocabulariesLoader(
        args.source,
        database_engine=engine,
        flush_interval=args.flush_interval,
        drop_constraints_and_indexes_before_insert=not args.keep_constraints,
        recreate_constraints_and_indexes_after_insert=not args.no_recreate,
        truncate_vocabulary_tables_before_insert=args.truncate,
        show_progress_bar=not args.no_progress,
        omop_module=omop,
        max_rows_pers_csv=args.max_rows,
        save_loader_state_into_table=not args.no_state,
        skip_invalid_foreign_keys=args.skip_invalid_foreign_keys,
        download_dir=args.download_dir,
        keep_download=args.keep_download,
    )
    if args.reset_state:
        loader.reset_state()
    loader.load_all()
    log.info("Done")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        if args.command == "load-vocab":
            load_vocab(args)
    except KeyboardInterrupt:
        again = "without --truncate " if args.truncate else ""
        print(f"Interrupted. Run the same command {again}again to continue.", file=sys.stderr)
        return 130
    except (
        ConstraintRecreateError,
        CsvFormatError,
        UnsupportedDatabaseError,
        VocabularyLoaderError,
        VocabularySourceError,
        DBAPIError,
    ) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
