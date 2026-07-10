import json
from pathlib import Path
from typing import List

from app.clients.instagram_client import InstagramClient
from app.models.user import User


class OfficialExportClient:
    def __init__(self, export_dir: Path):
        self.export_dir = Path(export_dir)

    def login(self) -> None:
        pass

    def _find_file(self, pattern: str) -> Path:
        matches = list(self.export_dir.rglob(pattern))
        if not matches:
            raise FileNotFoundError(f"Export file not found: {pattern} in {self.export_dir}")
        return matches[0]

    def _parse_username(self, href: str) -> str:
        """Extract username from Instagram profile URL."""
        return href.rstrip("/").split("/")[-1]

    def _read_followers(self) -> List[User]:
        path = self._find_file("followers_*.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        users: List[User] = []
        for item in data:
            for entry in item.get("string_list_data", []):
                username = entry.get("value") or self._parse_username(entry.get("href", ""))
                if username:
                    users.append(
                        User(
                            id=username,
                            username=username,
                            full_name="",
                            is_private=False,
                        )
                    )
        return users

    def _read_following(self) -> List[User]:
        path = self._find_file("following.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        users: List[User] = []
        for item in data.get("relationships_following", []):
            username = item.get("title", "")
            if not username and item.get("string_list_data"):
                username = self._parse_username(item["string_list_data"][0].get("href", ""))
            if username:
                users.append(
                    User(
                        id=username,
                        username=username,
                        full_name="",
                        is_private=False,
                    )
                )
        return users

    def get_followers(self) -> List[User]:
        return self._read_followers()

    def get_following(self) -> List[User]:
        return self._read_following()
