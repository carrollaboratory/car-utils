# `LinkMLModelLoader`

`car_utils.linkml.LinkMLModelLoader` attaches a LinkML-generated SQLAlchemy
model to a database connection, renaming its tables (and optionally its
schema) to match what your loading job actually needs -- for example, dbt's
`tgt_`-prefixed staging tables.

It does **not** create tables. The database must already have the target
tables (matching the prefixed/schema-qualified names it patches to) before
you load rows through it -- run the schema you were given against the
database first.

## Install

Example LinkML model and schema files:
- [SQL Alchemy Model](https://github.com/carrollaboratory/md-terminology-trove/releases/download/v0.1.1/md_terminology_trove-0.1.1-py3-none-any.whl)
- [PG+dbt_unit+LinkML safe example SQL Schema](https://github.com/carrollaboratory/md-terminology-trove/releases/download/v0.1.1/md_terminology_trove.sql)


You need both `car-utils` and the LinkML model package (see link above). The 
links above are linked to artifacts produced during the release. These will 
need to be updated whenever a new release is created. 

```
uv add car-utils
uv add https://github.com/carrollaboratory/md-terminology-trove/releases/download/v0.1.1/md_terminology_trove-0.1.1-py3-none-any.whl
```

or with `pip`:

```
pip install car-utils
pip install [/path/to/the_model-1.0.0-py3-none-any.whl](https://github.com/carrollaboratory/md-terminology-trove/releases/download/v0.1.1/md_terminology_trove-0.1.1-py3-none-any.whl)
```

Once it's installed, find the dotted import path you'll pass to the loader.
It's whatever top-level module/package the wheel installs -- check the
wheel's contents if you're not sure:

```
unzip -l /path/to/the_model-1.0.0-py3-none-any.whl | head
```

Look for a `.py` file (or package directory) at the top level, alongside the
`*.dist-info/` folder -- that name, without the `.py`, is the
`model_import_path`.

For md-terminology-trove, that would simply be "md_terminology_trove". This 
will be the library you import for the SQL Alchemy models. 

## Initialize the database

Run the schema you were given against the target database before loading
anything, e.g.:

```
psql "$DATABASE_URL" -f schema.sql
```

`LinkMLModelLoader` connects to and renames tables that must already exist;
it has no `create_all()` step.

## Quickstart

```python
from car_utils import LinkMLModelLoader, setup_logging

setup_logging(level="INFO")

loader = LinkMLModelLoader(
    database_url="postgresql://user:pass@localhost/warehouse",
    model_import_path="md_terminology_trove",   # the name you found in the wheel
    table_prefix="tgt_{}",           # note the `{}` -- see Gotchas below
    schema_name="staging",
).load()

Widget = loader.get_model("Widget")

with loader.create_session() as session:
    session.add(Widget(id="w1", name="example"))
    session.commit()

# Or stream existing rows in chunks instead of loading them all at once:
for widget in loader.stream("Widget", chunksize=1000):
    print(widget.id, widget.name)
```

## Constructor arguments

| Argument | Description |
|---|---|
| `database_url` | SQLAlchemy database URL, e.g. `postgresql://user:pass@host/db`. |
| `model_import_path` | Dotted import path to the installed model module (what you get from a wheel install). Mutually exclusive with `model_as_file`. |
| `model_as_file` | Dict describing a model file instead of an installed package -- see [Loading from a file](#loading-from-a-file-instead-of-a-wheel) below. Mutually exclusive with `model_import_path`. |
| `table_prefix` | Format string applied to each table name, e.g. `"tgt_{}"`. Default is `"tgt_"` -- **must contain a `{}` placeholder to work** (see Gotchas). |
| `schema_name` | Database schema to assign to the model's tables. Default `None` (use whatever the model's metadata already specifies). |
| `staging_dir` | Where GitHub-sourced model files are cached, only relevant to the `model_as_file` + `model_source` path. Default `"staging"` (relative to cwd). |

## Methods

- **`.load()`** -- opens the database engine, imports/loads the model
  module, patches its table names (and schema, if given), and sets up a
  session factory. Returns `self`, so it chains off the constructor. Call
  this before any of the methods below.
- **`.get_model(class_name)`** -- returns the ORM class by name, e.g.
  `loader.get_model("Widget")`.
- **`.create_session()`** -- returns a new SQLAlchemy `Session` bound to the
  loader's engine.
- **`.stream(class_name, chunksize=1000)`** -- generator that yields rows
  from the named model's table in chunks, using a `stream_results` cursor.
  Use this instead of `create_session()` + a manual query when reading a
  large existing table.

Also exported from `car_utils`, independently useful:

- **`get_model_pk(model_class)`** -- returns the list of primary-key column
  names for an ORM class.
- **`sync_github_file(owner, repo, path, ref="main", local_filepath=None)`**
  -- downloads a file from GitHub only if missing or out of date (compares
  git blob SHAs). Used internally by the `model_as_file` + `model_source`
  path; exposed because it's independently useful.

## Gotchas

### `table_prefix` needs a `{}` placeholder

`table_prefix` is used as a format string: `table_prefix.format(table_name)`.
If you pass a plain string with no `{}` in it -- including the **default**,
`"tgt_"` -- `str.format()` silently ignores the argument and *every table
collapses to that literal string*:

```python
>>> "tgt_".format("widget")
'tgt_'
>>> "tgt_{}".format("widget")
'tgt_widget'
```

Always pass an explicit `table_prefix="tgt_{}"` (or whatever prefix you
need) rather than relying on the default.

### Loading the same `model_import_path` twice in one process

`importlib.import_module` caches by dotted path, so a second
`LinkMLModelLoader` built against the same `model_import_path` gets the
*same* module object as the first -- and since patching mutates that
module's metadata in place, the second load re-patches the first load's
already-patched tables (prefixes compound, e.g. `b_a_widget` instead of
`b_widget`).

If your script only ever needs one loader for a given model, this doesn't
matter. If you need two loaders against the same model (e.g. two different
prefixes), use `model_as_file` instead -- each `model_as_file` load gets its
own fresh module object.

### Loading from a file instead of a wheel

If you're ever handed a loose model `.py` file rather than a wheel, use
`model_as_file` in place of `model_import_path`:

```python
loader = LinkMLModelLoader(
    database_url="postgresql://user:pass@localhost/warehouse",
    model_as_file={"model_filename": "the_model.py"},
    table_prefix="tgt_{}",
).load()
```

`model_as_file` also supports pulling the file from GitHub instead of
reading it off disk, by adding `model_source` (as `"owner/repo"`) and
`source_ref` (branch, tag, or commit SHA); the file is cached under
`staging_dir` and only re-downloaded when the remote copy changes.
