import io

import pytest
from databricks.sdk.service.files import DownloadResponse

from localbricks.files import InaccessibleFileLocationError, open_file


class FakeWorkspaceClient:
    def __init__(self, file_contents: dict[str, bytes]):
        self.files = FakeFilesAPI(file_contents)


class FakeFilesAPI:
    def __init__(self, contents: dict[str, bytes]):
        self.contents = contents

    def download(self, file_path: str) -> DownloadResponse:
        return DownloadResponse(contents=io.BytesIO(self.contents[file_path]))

    def upload(
        self,
        file_path: str,
        contents: io.BytesIO,
        overwrite: bool = True,
    ) -> None:
        self.contents[file_path] = contents.getvalue()


def test_open_file_invalid_path_raises_error():
    client = FakeWorkspaceClient({})
    with pytest.raises(InaccessibleFileLocationError):
        with open_file("/local_disk0", "r", client=client):
            pass


def test_open_file_read_text_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.txt"
    client = FakeWorkspaceClient({file_path: b"Hi, Mr. Fox!"})
    with open_file(file_path, "r", client=client) as f:
        assert f.read() == "Hi, Mr. Fox!"


def test_open_file_write_text_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.txt"
    client = FakeWorkspaceClient({})
    with open_file(file_path, "w", client=client) as f:
        f.write("Hi, Mr. Fox!")
    contents = client.files.contents[file_path]
    assert contents == b"Hi, Mr. Fox!"


def test_open_file_read_update_text_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.txt"
    client = FakeWorkspaceClient({file_path: b"Hi, Mr. Fox!"})
    with open_file(file_path, "r+", client=client) as f:
        read_contents = f.read()
        f.write(" This is Badger.")
    final_contents = client.files.contents[file_path]
    assert read_contents == "Hi, Mr. Fox!"
    assert final_contents == b"Hi, Mr. Fox! This is Badger."


def test_open_file_read_binary_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.bin"
    client = FakeWorkspaceClient({file_path: b"\x48\x69"})
    with open_file(file_path, "rb", client=client) as f:
        assert f.read() == b"\x48\x69"


def test_open_file_write_binary_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.bin"
    client = FakeWorkspaceClient({})
    with open_file(file_path, "wb", client=client) as f:
        f.write(b"\x48\x69")
    contents = client.files.contents[file_path]
    assert contents == b"\x48\x69"


def test_open_file_read_update_binary_mode():
    file_path = "/Volumes/my_catalog/my_schema/my_volume/test.bin"
    client = FakeWorkspaceClient({file_path: b"\x48\x69"})
    with open_file(file_path, "rb+", client=client) as f:
        read_contents = f.read()
        f.write(b"\x20\x42")
    final_contents = client.files.contents[file_path]
    assert read_contents == b"\x48\x69"
    assert final_contents == b"\x48\x69\x20\x42"
