import io
from databricks.sdk.service.files import DownloadResponse

from localbricks.files import open_file


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
