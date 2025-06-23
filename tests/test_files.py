import io


class FakeWorkspaceClient:
    def __init__(self):
        self.files = FakeFilesAPI()


class FakeFilesAPI:
    def __init__(self):
        self.files: dict[str, bytes] = {}

    def download(self, file_path: str) -> io.BytesIO:
        return io.BytesIO(self.files[file_path])

    def upload(
        self,
        file_path: str,
        contents: io.BytesIO,
        overwrite: bool = True,
    ) -> None:
        self.files[file_path] = contents.getvalue()
