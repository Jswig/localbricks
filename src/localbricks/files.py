import os
import io
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, IO, cast

import databricks.sdk

from .platform import is_databricks_driver


class InaccessibleFileLocationError(ValueError):
    """Raised when a file path refers to a location that is not accessible via the Databricks API"""


def _validate_mode(mode: str) -> None:
    """Validate file mode string.

    :param mode: Mode string to validate
    :raises ValueError: If mode is invalid
    """
    valid_chars = {"r", "w", "+", "b", "t"}
    if not set(mode) <= valid_chars:
        raise ValueError(
            f"Invalid mode: {mode}. Supported characters are: {', '.join(sorted(valid_chars))}"
        )
    if "b" in mode and "t" in mode:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must be either binary ('b') or text ('t', default), but not both"
        )
    base_modes = set(mode) & {"r", "w"}
    if len(base_modes) > 1:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must have exactly one base mode: 'r' (read), or 'w' (write)"
        )
    if not base_modes:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must include a base mode: 'r' (read), or 'w' (write)"
        )


def _validate_file_path(file_path: str | os.PathLike):
    file_path = Path(file_path) if not isinstance(file_path, Path) else file_path
    # The Databricks API requires an absolute path, so to make sure the code is portable
    # between Databricks and local environments, we can only allow absolute paths.
    # For the same reason, we only allow paths in the Workspace or Volumes, since these
    # are accessible via the API (unlike for instance, the local filesystem on a
    # cluster's driver node).
    #
    # file_path.parts[0] is '/'
    is_accessible_location = file_path.parts[1] in {"Volumes", "Workspace"}
    if not file_path.is_absolute() or not is_accessible_location:
        raise InaccessibleFileLocationError(
            "File path must be an absolute path to a file in the Databricks "
            "Workspace or a Unity Catalog Volume accessible from that workspace, "
            f"got {file_path}"
        )


@contextmanager
def open_file(
    file: str | os.PathLike,
    mode: str = "r",
    encoding: str = "utf-8",
    client: databricks.sdk.WorkspaceClient | None = None,
) -> Generator[IO, None, None]:
    """Provides a file-like interface to a file in a Databricks workspace or Volume.

    This aims to emulate the built-in 'open()' function. When running against a remote
    Databricks workspace, a few limitations need to be considered:

    - files are loaded entirely into memory
    - writes are buffered and changes are persisted to the Workspace or Volume
      only on context exit

    :param file: Path to the file to open
    :param mode: File mode ('r', 'w', 'r+', 'w+', with optional 'b' for binary
        or 't' for text, which is the default)
    :param encoding: Encoding for text files
    :param client: Databricks SDK client. If None, creates a new client using the
        default authentication method.
    :yields: File-like object
    :raises ValueError: If mode is invalid
    """
    _validate_file_path(file)
    _validate_mode(mode)

    if is_databricks_driver():
        # Use local filesystem when on Databricks driver
        opened_file = open(file, mode, encoding=encoding)
        try:
            yield opened_file
        finally:
            opened_file.close()
    else:
        if client is None:
            client = databricks.sdk.WorkspaceClient()

        file_path = str(file)
        is_binary_mode = "b" in mode
        is_read_mode = "r" in mode
        is_write_mode = "w" in mode
        is_update_mode = "+" in mode

        if is_read_mode:
            response = client.files.download(file_path)
            if response.contents is None:
                raise ValueError(f"No contents for {file_path}")
            if is_binary_mode:
                opened_file = response.contents
            else:
                text = response.contents.read().decode(encoding)
                opened_file = io.StringIO(text)
        else:
            if is_binary_mode:
                opened_file = io.BytesIO()
            else:
                opened_file = io.StringIO()

        try:
            yield opened_file

            if is_write_mode or is_update_mode:
                if is_binary_mode:
                    # TODO: these type casts are not very elegant, it may be cleaner to
                    # satisfy mypy by using a separate function for each type of content
                    opened_file = cast(io.BytesIO, opened_file)
                    upload_contents = opened_file
                else:
                    opened_file = cast(io.StringIO, opened_file)
                    upload_contents = io.BytesIO(
                        opened_file.getvalue().encode(encoding)
                    )
                client.files.upload(file_path, upload_contents, overwrite=True)
        finally:
            opened_file.close()
