from pathlib import Path

from .mock_client import MockClient


class ArchiveClient(MockClient):
    def __init__(
        self,
        followers_file: Path = Path("data/export/followers.json"),
        following_file: Path = Path("data/export/following.json"),
    ):
        super().__init__(followers_file, following_file)
