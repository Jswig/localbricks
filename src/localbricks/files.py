import os
import io
from contextlib import contextmanager
from typing import Generator, IO

import databricks.sdk

from .platform import is_databricks_driver


def _validate_mode(mode: str) -> None:
    """Validate file mode string.
    
    :param mode: Mode string to validate
    :raises ValueError: If mode is invalid
    """
    valid_chars = {"r", "w", "a", "+", "b", "t"}
    if not set(mode) <= valid_chars:
        raise ValueError(
            f"Invalid mode: {mode}. Supported characters are: {', '.join(sorted(valid_chars))}"
        )
    # Check for conflicting binary/text modes
    if "b" in mode and "t" in mode:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must be either binary ('b') or text ('t', default), but not both"
        )
    # Validate mode combinations
    base_modes = set(mode) & {"r", "w", "a"}
    if len(base_modes) > 1:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must have exactly one base mode: 'r' (read), 'w' (write), or 'a' (append)"
        )
    if not base_modes:
        raise ValueError(
            f"Invalid mode: {mode}. "
            "Mode must include a base mode: 'r' (read), 'w' (write), or 'a' (append)"
        )


def _validate_file_path(file: str | os.PathLike):
    if not os.path.isabs(file):
        raise ValueError(f"File path must be absolute: {file}")


@contextmanager
def open_file(
    file: str | os.PathLike,
    mode: str = "r",
    encoding: str = "utf-8",
    client: databricks.sdk.WorkspaceClient | None = None,
) -> Generator[IO, None, None]:
    """Provides a file-like interface to a file in the Databricks Workspace.

    This aims to emulate the built-in 'open()' function.

    :param file: Path to the file to open
    :param mode: File mode ('r', 'w', 'a', 'r+', 'w+', 'a+', with optional 'b' for binary)
    :param encoding: Encoding for text files (default: utf-8)
    :param client: Databricks SDK client. If None, creates a new client using the
        default authentication method.
    :yields: File-like object (StringIO/BytesIO when not on Databricks)
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

        is_binary_mode = 'b' in mode
        is_read_mode = 'r' in mode
        is_write_mode = 'w' in mode
        is_update_mode = '+' in mode

        if is_read_mode or is_update_mode:
            # Download existing file content
            response = client.files.download(file)   
            if is_binary_mode:
                opened_file = response.contents
            else:
                text = response.contents.read().decode(encoding)
                opened_file = io.StringIO(text)
        else:
            # Create new file buffer
            if is_binary_mode:
                opened_file = io.BytesIO()
            else:
                opened_file = io.TextIO()

        try:
            yield opened_file

            if is_write_mode or is_update_mode:
                if is_binary_mode:
                    upload_contents = opened_file
                else:
                    upload_contents = io.BytesIO(
                        opened_file.getvalue().encode(encoding)
                    )
                client.files.upload(file, upload_contents, overwrite=True)
        finally:
            opened_file.close()
