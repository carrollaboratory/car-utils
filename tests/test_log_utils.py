import logging

from car_utils.log_utils import is_interactive, setup_logging


def test_is_interactive_returns_a_bool():
    assert isinstance(is_interactive(), bool)


def test_setup_logging_creates_the_log_file(tmp_path):
    log_file = tmp_path / "nested" / "log.txt"
    setup_logging(level="DEBUG", log_file=str(log_file))
    logging.getLogger(__name__).info("hello")
    assert log_file.exists()


def test_setup_logging_without_a_log_file_does_not_touch_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    setup_logging(level="INFO", log_file=None)
    assert list(tmp_path.iterdir()) == []
