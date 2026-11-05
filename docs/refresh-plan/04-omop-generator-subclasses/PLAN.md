# Session 04 – OMOP Generator Subclasses

**Goal:** remove all text post-processing. The OMOP-specific choices live in one readable
policy file, applied by subclasses of the sqlacodegen generators.

## Tasks

- [x] Extend `generator/src/omop_codegen/omop_policy.py`. It holds plain data, no logic:
  - `CANDIDATE_KEYS`: table → columns *(done in S03)*
  - `DROP_REVERSE_RELATIONSHIPS`: for example "no `List[...]` back-references on
    `Concept`, `Domain`, `Vocabulary`, `ConceptClass` except …"
    *(→ `NO_REVERSE_RELATIONSHIPS` + `SELF_REFERENCE_REVERSE_RELATIONSHIPS`. Only `Concept` needs it)*
  - `RELATIONSHIP_NAMES`: explicit names for ambiguous multi-FK cases
    (`ConceptRelationship.concept_1/concept_2`, `FactRelationship.domain_concept_1/2`, …).
    Copy them from today's `_hotfixes()`. *(not needed: `nofknames` gives every name. Pinned by a test)*
- [x] `OmopGeneratorMixin` with overrides for:
  - `generate_relationship_name()`: pluralize lists, apply `RELATIONSHIP_NAMES`, handle `_reverse`
  - The relationship generation step: drop the reverse sides listed in the policy and remove
    their `back_populates` counterpart (replaces `remove_excessive_backpopulate` and `remove_reverse_1to1`)
  - `render_relationship_arguments()`: always give `foreign_keys` when the target has more than one FK path
    *(no override: sqlacodegen 4 does it)*
  - Class rendering: `__mapper_args__ = {"primary_key": [...]}` for candidate keys
  - Module header: license, CDM release tag, sqlacodegen version
- [x] Concrete classes for all four flavors (D2): `OmopTablesGenerator`, `OmopDeclarativeGenerator`,
      `OmopDataclassGenerator`, `OmopSQLModelGenerator`.
- [x] Relationship names must match the baseline exactly (D4). Start with `nofknames` and add
      `RELATIONSHIP_NAMES` entries for whatever is left.
- [x] Delete `generator/legacy_post_processing/` (`pre_gen_sql/` is gone since S03).
- [x] Fix the inconsistency where `Concept.concept_classes` has `back_populates` but the
      other side doesn't.

## Done when

- The baseline diff is **empty**, except for entries in the "allowed differences" list, each
  with a reason (bug fix or agreed decision)
- The smoke tests pass for every kept flavor

## Risks

- sqlacodegen's internal model (`RelationshipAttribute`, `ModelClass`) isn't a stable API.
  Pin the version and add a test that fails loudly when an upgrade changes the output.
