"""Generates the dzdomop models from the official OMOP CDM DDL.

Pipeline: download ─▶ deploy DDL to Postgres ─▶ reflect MetaData ─▶ enrich
─▶ sqlacodegen (library) ─▶ write. Entry point: ``omop-codegen`` (see ``cli.py``).
"""
