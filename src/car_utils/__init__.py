from importlib.metadata import PackageNotFoundError, version

from .linkml import LinkMLModelLoader, get_model_pk, sync_github_file
from .log_utils import is_interactive, setup_logging

try:
    __version__ = version("car-utils")
except PackageNotFoundError:
    # Fallback for when the package is imported locally without being installed
    __version__ = "0.0.0-unknown"

__all__ = [
    "LinkMLModelLoader",
    "get_model_pk",
    "is_interactive",
    "setup_logging",
    "sync_github_file",
]
