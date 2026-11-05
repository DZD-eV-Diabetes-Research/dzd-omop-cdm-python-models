"""The CDM versions we generate, and where their files are in a release archive."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The order the official scripts must run in.
DDL_PARTS = ("ddl", "primary_keys", "indices", "constraints")


@dataclass(frozen=True)
class CdmVersion:
    name: str  # "5.4"

    @property
    def module_prefix(self) -> str:
        """``OMOP_5_4``: prefix of the generated module names."""
        return "OMOP_" + self.name.replace(".", "_")

    def ddl_files(self, release_dir: Path) -> list[Path]:
        ddl_dir = release_dir / "inst" / "ddl" / self.name / "postgresql"
        return [ddl_dir / f"OMOPCDM_postgresql_{self.name}_{part}.sql" for part in DDL_PARTS]

    def table_csv(self, release_dir: Path) -> Path:
        return release_dir / "inst" / "csv" / f"OMOP_CDMv{self.name}_Table_Level.csv"

    def field_csv(self, release_dir: Path) -> Path:
        return release_dir / "inst" / "csv" / f"OMOP_CDMv{self.name}_Field_Level.csv"


CDM_VERSIONS: dict[str, CdmVersion] = {v.name: v for v in (CdmVersion("5.3"), CdmVersion("5.4"))}
