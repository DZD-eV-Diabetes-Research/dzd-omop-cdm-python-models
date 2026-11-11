# Run with Docker

Needs [Docker](https://docs.docker.com/get-started/get-docker/) with `docker compose`. From the
repository root:

```bash
./run_codegen.sh
```

This regenerates every module and **overwrites** the committed models in
`packages/dzdomop/src/omopmodel/`. Review the result with `git diff` and run the
[tests](07-testing.md).

## What the script does

[`run_codegen.sh`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/run_codegen.sh)
drives [`docker-compose.yaml`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/docker-compose.yaml):

| Step | Command |
| ---- | ------- |
| Clean up a previous run | `docker compose down --remove-orphans` |
| Create `downloads/` as your user (Docker would create it as root) | `mkdir -p downloads` |
| Build the generator image | `docker compose build` |
| Start Postgres and the generator | `docker compose up -d` |
| Follow the generator's log until it exits | `docker compose logs -f omopcodegen` |
| Stop Postgres | `docker compose down` |

| Service | What it is |
| ------- | ---------- |
| `postgresql` | `postgres:16`, user, password and database `omop`. No port is published. |
| `omopcodegen` | Built from the [`dockerfile`](https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models/blob/beta/dockerfile): Python 3.12, the generator with the locked dependencies from `uv.lock`. Starts when Postgres is healthy. |

| Folder on the host | In the container | Holds |
| ------------------ | ---------------- | ----- |
| `packages/dzdomop/src/omopmodel/` | `/output` | the generated modules |
| `downloads/` | `/downloads` | the cached CDM release (git ignores it) |

The first run builds the image and downloads the release. Later runs reuse both.

> [!NOTE]
> The script exits with 0 even when the generator fails. Read the end of the log: a
> successful run ends with one `Wrote /output/OMOP_...py` line per module. A failed run changes no file.

## File owner: UID and GID

The generator container runs as `${UID:-1000}:${GID:-1000}`. Bash doesn't export `UID` and
doesn't set `GID` at all, so by default the files belong to 1000:1000. If your user has other
IDs, export them first:

```bash
export UID GID=$(id -g)
./run_codegen.sh
```

## Other settings

The container gets its settings from the `environment:` of `omopcodegen` in
`docker-compose.yaml` (see [Configuration](04-configuration.md)). To generate only some
versions or flavors, or into another folder, [run it locally](03-run-locally.md): that's
quicker than editing the compose file.
