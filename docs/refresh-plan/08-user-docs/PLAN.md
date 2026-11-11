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

- [ ] Write the pages above
- [ ] Trim the root `README.md` to a pitch + a 10-line quickstart + links. Merge
      `README_codegen.md` and `DZDOMOPModel/README.md` into the docs and delete them.
- [ ] Optional: an mkdocs-material site (the extras are already in `pyproject.toml`), published
      with GitHub Pages
- [ ] Run the snippets in the docs as tests (e.g. `pytest-examples` or `pytest --doctest-glob`)

## Done when

- A new user gets from zero to "Person in SQLite" with only `docs/models/02-quickstart.md`
- A contributor can add a CDM version with only `docs/generator/06-new-cdm-version.md`
