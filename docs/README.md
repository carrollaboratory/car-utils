# car-utils

Common Python utilities for Carroll lab tools -- shared infrastructure code
with no domain logic of its own, so it can sit underneath multiple
unrelated projects (currently [spit-fhir](https://github.com/carrollaboratory/spit-fhir)
and a coworker's warehouse-population job) without coupling them together.

Deliberately kept small: only things that are genuinely reusable across
unrelated tools belong here. Domain-specific code (FHIR handling, dbt-shaped
assumptions, etc.) belongs in the tool that owns that domain.

## What's here

- **`car_utils.log_utils`** -- `setup_logging()` / `is_interactive()`.
  Rich-formatted logs in an interactive terminal, plain formatted logs
  (console + optional file) otherwise.
- **`car_utils.linkml`** -- `LinkMLModelLoader`, for attaching a
  LinkML-generated SQLAlchemy model to a database and patching table
  names/schema to match what dbt produced. Also `get_model_pk()` and
  `sync_github_file()` (used internally, exposed since they're independently
  useful). See the class docstring for a real limitation around reusing a
  loader with `model_import_path` more than once per process.

## Install

```
just install    # uv sync --extra dev
```

Requires Python 3.13+.

## Test

```
just test
```
