import json
from pathlib import Path
from typing import List

from app.models.user import User


class MockClient:
    def __init__(self, followers_path: Path, following_path: Path):
        self.followers_path = Path(followers_path)
        self.following_path = Path(following_path)

    def login(self) -> None:
        pass

    def _load(self, path: Path) -> List[User]:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [User.from_dict(item) for item in data]

    def get_followers(self) -> List[User]:
        return self._load(self.followers_path)

    def get_following(self) -> List[User]:
        return self._load(self.following_path)

    def get_blocked(self) -> List[User]:
        return []

    def get_hide_story_from(self) -> List[User]:
        return []

    def get_recently_unfollowed(self) -> List[User]:
        return []

    def get_recent_follow_requests(self) -> List[User]:
        return []
