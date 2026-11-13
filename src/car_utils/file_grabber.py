"""Helper function to pull content from files remote or local."""

import contextlib
import io
from collections.abc import Generator
from pathlib import Path
from typing import IO

import httpx


@contextlib.contextmanager
def open_archive_buffer(
    path_or_url: str | Path, client: httpx.Client | None = None
) -> Generator[IO[bytes], None, None]:
    """Establishes a context manager returning a readable bytes buffer
    from either a local file path or a remote URL.
    """
    path_str = str(path_or_url)

    # Remote URL
    if path_str.startswith(("http://", "https://")):
        # Use provided client or spin up an ephemeral one
        close_client = False
        if client is None:
            client = httpx.Client(http2=True, follow_redirects=True)
            close_client = True

        try:
            # Stream the response to keep memory profile predictable
            with client.stream("GET", path_str) as response:
                response.raise_for_status()
                # Yield the raw response stream (duck-types as a binary IO buffer)
                yield io.BytesIO(response.content)
        finally:
            if close_client:
                client.close()

    # Local File
    else:
        local_path = Path(path_str).resolve()
        if not local_path.is_file():
            raise FileNotFoundError(f"Archive not found at: {local_path}")

        with open(local_path, "rb") as f:
            yield f
