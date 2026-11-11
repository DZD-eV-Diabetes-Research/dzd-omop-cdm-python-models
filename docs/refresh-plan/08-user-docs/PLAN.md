# Session 08 – User Documentation

**Goal:** two short, friendly guides: one for people who *use the models*, one for people who
*run the generator*. Many small pages, each one a quick read.

## Style rules

- One topic per page, about 1–2 screens
- Code first, explanation second
- Every snippet is copy-paste runnable, and tested (see below)
- Short sentences. Tables beat paragraphs. No walls of text.

## Structure

```
docs/
├── index.md                    # What is this? Which guide do I need?
├── models/
│   ├── 01-install.md           # pip install + extras
│   ├── 02-quickstart.md        # create the schema, insert a person, query it (5 min)
│   ├── 03-pick-a-flavor.md     # sqlmodel vs declarative (vs dataclasses): one table
│   ├── 04-relationships.md     # person.care_site, care_site.persons, concept lookups
│   ├── 05-validation.md        # what is and isn't checked, model_validate
│   ├── 06-vocabulary.md        # load an Athena export (folder, zip, URL), resume, speed tips
│   ├── 07-postgres.md          # schemas, drivers, performance
│   └── faq.md
└── generator/
    ├── 01-overview.md          # pipeline diagram, what each step does
    ├── 02-run-with-docker.md   # one command
    ├── 03-run-locally.md       # uv + your own Postgres, env vars
    ├── 04-configuration.md     # table of all settings
    ├── 05-omop-policy.md       # how to change relationships, names and candidate keys
    ├── 06-new-cdm-version.md   # checklist for adding a new CDM release
    └── 07-testing.md           # baseline snapshots, allowed differences
```

## Tasks

- [x] Write the pages above
- [x] Trim the root `README.md` to a pitch + a 10-line quickstart + links. Merge
      `README_codegen.md` into the docs and delete it. *(Corrected: `DZDOMOPModel/README.md` is
      now `packages/dzdomop/README.md`, the PyPI page; it can't be deleted, so it became a short
      version of the root README with absolute links. `examples/` and `load_vocab.png` deleted.)*
- [x] A docs site published with GitHub Pages. *(Corrected: there were no mkdocs extras.
      mkdocs-material is out of support since 2026-11-05, so the site uses its successor
      Zensical: `zensical.toml`, dependency group `docs`, workflow `docs.yml`.)*
- [x] Run the snippets in the docs as tests *(own file `tests/test_docs.py`, Tim's choice)*

## Done when

- A new user gets from zero to "Person in SQLite" with only `docs/models/02-quickstart.md`
- A contributor can add a CDM version with only `docs/generator/06-new-cdm-version.md`
