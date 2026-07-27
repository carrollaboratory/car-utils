from pathlib import Path

from sqlalchemy import select

from car_utils.linkml import LinkMLModelLoader, get_model_pk

FIXTURE = "tests/fixtures/toy_model.py"


def test_load_and_query(tmp_path):
    loader = LinkMLModelLoader(
        database_url="sqlite:///:memory:",
        model_as_file={"model_filename": FIXTURE},
        table_prefix="tgt_{}",
        staging_dir=tmp_path,
    ).load()

    widget = loader.get_model("Widget")
    assert get_model_pk(widget) == ["id"]
    assert "tgt_widget" in str(select(widget))


def test_staging_dir_is_per_instance_not_shared_on_the_class(tmp_path):
    """Regression test: staging_dir used to be set as a class attribute
    inside __init__, so two loaders would stomp on each other's staging dir."""
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"

    loader_a = LinkMLModelLoader(
        model_as_file={"model_filename": FIXTURE}, staging_dir=dir_a
    )
    loader_b = LinkMLModelLoader(
        model_as_file={"model_filename": FIXTURE}, staging_dir=dir_b
    )

    assert loader_a.staging_dir == dir_a
    assert loader_b.staging_dir == dir_b
    assert not hasattr(LinkMLModelLoader, "staging_dir")


def test_file_based_loaders_do_not_interfere_with_each_other(tmp_path):
    """Two model_as_file loaders in the same process should each get a fresh
    module -- confirmed by each ending up with its own table prefix rather
    than compounding the other's."""
    loader_a = LinkMLModelLoader(
        database_url="sqlite:///:memory:",
        model_as_file={"model_filename": FIXTURE},
        table_prefix="a_{}",
        staging_dir=tmp_path,
    ).load()
    loader_b = LinkMLModelLoader(
        database_url="sqlite:///:memory:",
        model_as_file={"model_filename": FIXTURE},
        table_prefix="b_{}",
        staging_dir=tmp_path,
    ).load()

    assert loader_a.module is not loader_b.module
    assert "a_widget" in str(select(loader_a.get_model("Widget")))
    assert "b_widget" in str(select(loader_b.get_model("Widget")))


def test_import_path_reuse_in_one_process_compounds_the_prefix(monkeypatch):
    """Known limitation, not a bug to silently regress on: importlib caches
    the module by dotted path, so a second loader against the same
    import_path re-patches the first loader's already-patched tables.

    Uses its own fixture module (distinct from FIXTURE's stem) so this test
    doesn't depend on sys.modules state left behind by the file-based tests.
    """
    monkeypatch.syspath_prepend("tests/fixtures")

    loader_a = LinkMLModelLoader(
        database_url="sqlite:///:memory:",
        model_import_path="toy_model_importable",
        table_prefix="a_{}",
    ).load()
    loader_b = LinkMLModelLoader(
        database_url="sqlite:///:memory:",
        model_import_path="toy_model_importable",
        table_prefix="b_{}",
    ).load()

    assert loader_a.module is loader_b.module
    assert "b_a_widget" in str(select(loader_b.get_model("Widget")))
