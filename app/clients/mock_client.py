import json
from pathlib import Path
from typing import List

from app.models.user import User


class MockClient:
    def __init__(self, followers_file: Path, following_file: Path):
        self.followers_file = Path(followers_file)
        self.following_file = Path(following_file)

    def login(self) -> None:
        pass

    def _load_users(self, path: Path) -> List[User]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return [User.from_dict(u) for u in data]

    def get_followers(self) -> List[User]:
        return self._load_users(self.followers_file)

    def get_following(self) -> List[User]:
        return self._load_users(self.following_file)
