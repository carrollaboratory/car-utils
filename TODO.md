# TODO

## Ported from piper, with fixes

`LinkMLModelLoader` and the logging setup came from
[carrollaboratory/piper](https://github.com/carrollaboratory/piper) (now
frozen/archived as a reference for the retired Jinja-based transform). Two
real bugs were fixed during the port, not just carried over:

- `staging_dir` used to be set as a *class* attribute from inside
  `__init__`, so two `LinkMLModelLoader` instances in the same process would
  stomp on each other's staging directory. Now an instance attribute
  (regression-tested in `test_staging_dir_is_per_instance_not_shared_on_the_class`).
- `is_interactive()` raised `io.UnsupportedOperation` whenever `sys.stdin`
  doesn't have a real file descriptor (pytest's captured stdin, some
  CI/subprocess setups) instead of just returning `False`. Now caught.

## Known limitation, not a bug

Loading the same `model_import_path` twice in one process compounds the
table prefix (`importlib.import_module` returns the same cached module both
times). `model_as_file` doesn't have this problem across independent calls,
but shares the same underlying risk if a file's stem happens to collide with
another load's import path (both end up keyed in `sys.modules`). See the
`LinkMLModelLoader` docstring and `tests/test_linkml.py` for the exact
behavior. Not fixing this now -- would need per-load isolated metadata/module
namespaces, and no current consumer needs more than one load per process.

## Not done yet

- No CI workflow.
- Nothing here yet for the coworker's warehouse-population job beyond what's
  already used by piper/spit-fhir -- add things as a second real consumer
  actually needs them, not speculatively.
