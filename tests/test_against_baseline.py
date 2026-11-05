"""Diff a fresh snapshot of every generated module against ``tests/baseline/``.

The baseline is the model surface as it was before the refresh. Every difference must
either go away or be listed in ``ALLOWED_DIFFERENCES`` with a reason.

Refresh a baseline only on purpose (e.g. a new CDM version)::

    python tools/snapshot_models.py OMOP_5_5_sqlmodels -o tests/baseline/OMOP_5_5_sqlmodels.json
"""

from __future__ import annotations

import json
from fnmatch import fnmatchcase
from pathlib import Path

import pytest
from baseline_diff import diff
from helpers import MODULES
from snapshot_models import snapshot_in_subprocess

BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

# Paths that say how the snapshot was taken, not what the models look like.
IGNORED_PATHS = ("snapshot_env", "snapshot_env.*")

# (module glob, path glob, reason). Paths look like the ones in the diff output, e.g.
#   ("OMOP_5_*_tables", "table_vars.t_metadata", "B1: ..."),
# A path ending in " (order)" matches a change in key order only.
_DEATH = (
    "Death.person / Person.death: real one-to-one instead of the old inheritance glitch (Tim, S04)"
)
_SQLMODEL_BACKREFS = (
    "sqlmodels gets the back-references declarative already has. The SQLModel-only "
    "hotfix worked around missing foreign_keys in sqlacodegen 3"
)
_UPSTREAM_INDEX = "upstream: index name typo fixed (vocabluary -> vocabulary)"
_UPSTREAM_FK = "upstream: new foreign key (episode.episode_parent_id, note_nlp.note_id)"
ALLOWED_DIFFERENCES: list[tuple[str, str, str]] = [
    # B8: comment format fixed (labels, empty parts, quotes)
    ("OMOP_5_*", "tables.*.comment", "B8"),
    ("OMOP_5_*", "tables.*.columns.*.comment", "B8"),
    # B1: the `metadata` table variable no longer overwrites the MetaData object
    ("OMOP_5_*_tables", "notes", "B1: module imports without the in-memory rename"),
    ("OMOP_5_*_tables", "table_vars.t_metadata", "B1: snapshot's in-memory name is gone"),
    ("OMOP_5_*_tables", "module_objects.t_metadata", "B1: snapshot's in-memory name is gone"),
    ("OMOP_5_*_tables", "table_vars.metadata_table", "B1: new name of the `metadata` table"),
    ("OMOP_5_*_tables", "module_objects.metadata_table", "B1: new name of the `metadata` table"),
    # Death <-> Person
    ("OMOP_5_*", "classes.Death.relationships.person", _DEATH),
    ("OMOP_5_*", "classes.Person.relationships.death", _DEATH),
    # Both sides of ConceptClass.concept_class_concept <-> Concept.concept_classes now
    # back-populate each other. Before, only Concept.concept_classes did (S04 plan).
    (
        "OMOP_5_*",
        "classes.ConceptClass.relationships.concept_class_concept.back_populates",
        "one-sided back_populates fixed",
    ),
    (
        "OMOP_5_*_sqlmodels",
        "classes.Concept.relationships.concept_classes.back_populates",
        "one-sided back_populates fixed",
    ),  # fmt: skip
    ("OMOP_5_*_sqlmodels", "classes.Domain.relationships.concepts", _SQLMODEL_BACKREFS),
    ("OMOP_5_*_sqlmodels", "classes.Vocabulary.relationships.concepts", _SQLMODEL_BACKREFS),
    (
        "OMOP_5_*_sqlmodels",
        "classes.Concept.relationships.domain.back_populates",
        _SQLMODEL_BACKREFS,
    ),  # fmt: skip
    (
        "OMOP_5_*_sqlmodels",
        "classes.Concept.relationships.vocabulary.back_populates",
        _SQLMODEL_BACKREFS,
    ),  # fmt: skip
    # B11: NOT NULL columns were nullable in the SQLModel flavor
    ("OMOP_5_*_sqlmodels", "tables.*.columns.*.nullable", "B11"),
    # B12: self-references pointed the wrong way in the SQLModel flavor
    ("OMOP_5_*_sqlmodels", "classes.VisitDetail.relationships.*.direction", "B12"),
    ("OMOP_5_*_sqlmodels", "classes.VisitOccurrence.relationships.*.direction", "B12"),
    # One `metadata` for every flavor: `omop.metadata.create_all(engine)`
    ("OMOP_5_*", "module_objects.metadata", "same MetaData name in every flavor (S05)"),
    # B2: dataclasses need only the NOT NULL columns. Nullable columns default to None, lists
    # to [], many-to-one / one-to-one relationships are no __init__ arguments (init=False)
    ("OMOP_5_*_dataclasses", "classes.*.init_required.*", "B2"),
    # B4: SQLModel classes derive from the module's own Base (own registry and MetaData)
    ("OMOP_5_*_sqlmodels", "classes.*.bases", "B4"),
    # sqlacodegen 4: `'Concept'` instead of `Optional['Concept']` for NOT NULL foreign keys,
    # like the declarative flavor (Tim, S04)
    ("OMOP_5_*_sqlmodels", "classes.*.relationships.*.python_type", "sqlacodegen 4 types"),
    # Upstream DDL changes between the releases v5.4.1 and v5.5.0 (S06)
    ("OMOP_5_[34]_*", "tables.concept.indexes.idx_concept_vocabluary_id", _UPSTREAM_INDEX),
    ("OMOP_5_[34]_*", "tables.concept.indexes.idx_concept_vocabulary_id", _UPSTREAM_INDEX),
    ("OMOP_5_4_*", "tables.episode.foreign_keys.fpk_episode_episode_parent_id", _UPSTREAM_FK),
    ("OMOP_5_4_*", "classes.Episode.relationships.episode_parent", _UPSTREAM_FK),
    ("OMOP_5_4_*", "tables.note_nlp.foreign_keys.fpk_note_nlp_note_id", _UPSTREAM_FK),
    ("OMOP_5_4_*", "classes.Note.relationships.note_nlps", _UPSTREAM_FK),
    ("OMOP_5_4_*", "classes.NoteNlp.relationships.note", _UPSTREAM_FK),
]


def is_allowed(module: str, path: str) -> bool:
    if any(fnmatchcase(path, p) for p in IGNORED_PATHS):
        return True
    return any(
        fnmatchcase(module, mod) and fnmatchcase(path, pat) for mod, pat, _ in ALLOWED_DIFFERENCES
    )


def test_every_module_has_a_baseline():
    baselines = sorted(p.stem for p in BASELINE_DIR.glob("*.json"))
    assert baselines == MODULES


@pytest.mark.parametrize("module", MODULES)
def test_snapshot_matches_baseline(module):
    baseline = json.loads((BASELINE_DIR / f"{module}.json").read_text(encoding="utf-8"))
    current = snapshot_in_subprocess(module)
    unexplained = [(p, d) for p, d in diff(baseline, current) if not is_allowed(module, p)]
    if unexplained:
        lines = "\n".join(f"  {p}: {d}" for p, d in unexplained[:200])
        more = f"\n  ... and {len(unexplained) - 200} more" if len(unexplained) > 200 else ""
        pytest.fail(
            f"{module}: {len(unexplained)} unexplained differences\n{lines}{more}", pytrace=False
        )
