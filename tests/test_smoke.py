"""Smoke tests for every generated model module.

Known bugs are ``xfail(strict=True)``: they must fail, and only in the way the bug
predicts (see ``BUG_SIGNATURES``). When a later fix makes one pass, the test turns red
on purpose. Then remove its entry from ``KNOWN_BUGS``.
"""

from __future__ import annotations

import pytest
from helpers import MODULES, KnownBug, run_check

# (check, flavor) -> bug ID. Empty: B2 and B4 are fixed.
KNOWN_BUGS: dict[tuple[str, str], str] = {}

FLAVORS = sorted({m.rsplit("_", 1)[1] for m in MODULES})


def flavor_of(module: str) -> str:
    return module.rsplit("_", 1)[1]


def params(check: str, items: list[str], flavor=flavor_of):
    out = []
    for item in items:
        bug = KNOWN_BUGS.get((check, flavor(item)))
        marks = [pytest.mark.xfail(raises=KnownBug, strict=True, reason=bug)] if bug else []
        out.append(pytest.param(item, bug, marks=marks, id=item))
    return out


@pytest.mark.parametrize(("module", "bug"), params("create_all", MODULES))
def test_import_and_create_all(module, bug):
    run_check("create_all", module, known_bug=bug)


@pytest.mark.parametrize(("module", "bug"), params("insert_person", MODULES))
def test_insert_person_and_care_site(module, bug):
    run_check("insert_person", module, known_bug=bug)


ORM_MODULES = [m for m in MODULES if flavor_of(m) != "tables"]


@pytest.mark.parametrize(("module", "bug"), params("vocabulary", ORM_MODULES))
def test_concept_vocabulary_relationship(module, bug):
    run_check("vocabulary", module, known_bug=bug)


@pytest.mark.parametrize(("flavor", "bug"), params("import_together", FLAVORS, flavor=lambda f: f))
def test_two_cdm_versions_in_one_process(flavor, bug):
    modules = [m for m in MODULES if flavor_of(m) == flavor]
    assert len(modules) > 1
    run_check("import_together", *modules, known_bug=bug)


@pytest.mark.parametrize(("module", "bug"), params("module_variables", MODULES))
def test_module_variables(module, bug):
    run_check("module_variables", module, known_bug=bug)


@pytest.mark.parametrize(("module", "bug"), params("docstrings", MODULES))
def test_docstrings(module, bug):
    run_check("docstrings", module, known_bug=bug)


@pytest.mark.parametrize(
    ("module", "bug"),
    params("sqlmodel_validation", [m for m in MODULES if flavor_of(m) == "sqlmodels"]),
)
def test_sqlmodel_validation(module, bug):  # B9
    run_check("sqlmodel_validation", module, known_bug=bug)


def test_package_import_keeps_global_sqlmodel_metadata_clean():  # B3
    run_check("package_import")


def test_bare_package_import_needs_no_extras():
    run_check("bare_package_import")


@pytest.mark.parametrize(
    ("module", "bug"),
    params("import_without_extras", [m for m in MODULES if flavor_of(m) != "sqlmodels"]),
)
def test_import_without_extras(module, bug):
    run_check("import_without_extras", module, known_bug=bug)
