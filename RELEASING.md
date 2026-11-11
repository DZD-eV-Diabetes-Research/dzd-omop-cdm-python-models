# Releasing

For maintainers. The package version comes from the git tag (hatch-vcs); there is no version
number in a file.

## Branches

| Branch | What | Docs |
| ------ | ---- | ---- |
| `main` | the released state | https://dzd-ev-diabetes-research.github.io/dzd-omop-cdm-python-models/ |
| `beta` | the next release: work lands here by pull request | the same site under `/beta/`, with a preview notice on every page |

A push to `main` or `beta` rebuilds both parts of the site (`tools/build_site.py`, run by
`.github/workflows/docs.yml`). Preview locally:

```bash
uv run --group docs python tools/build_site.py --stable main --preview beta
```

After a release, bring `beta` up to `main` (`git branch -f beta main`, push) so the preview
starts from the released state.

## Release candidate

1. On `beta`: tests green, `CHANGELOG.md` has the new version as `## X.Y.Z (unreleased)`, and
   `docs/upgrading.md` has a section for every change users must make.
2. Tag the commit: `git tag -a X.Y.ZrcN -m X.Y.ZrcN <commit>`, `git push origin X.Y.ZrcN`.
3. Create a GitHub release from the tag and tick **Set as a pre-release**. Publishing it runs
   `.github/workflows/publish-pypi.org.yaml`, which uploads to PyPI (trusted publishing,
   environment `pypi`).
4. Check: `pip install --pre dzdomop` in a fresh venv, run the quickstart.

`pip install dzdomop` ignores release candidates; only `--pre` or `==X.Y.ZrcN` installs them.

## Release

1. On `beta`: a commit that sets the date, `## X.Y.Z (YYYY-MM-DD)`.
2. Pull request `beta` → `main`, merge it with a **merge commit** (not squash or rebase).
3. Tag the merge commit on `main` with `X.Y.Z` and create a GitHub release (latest) from it.
4. Check: `pip install dzdomop` in a fresh venv, run the quickstart.

Put every tag on its own commit: two version tags on the same commit make the version that
hatch-vcs picks ambiguous. That's why the final release isn't tagged on the release
candidate's commit.

Release titles so far are the version plus a quote from a well-known film, e.g.
"0.5.0: You're gonna need a bigger boat.".
