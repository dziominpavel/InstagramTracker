import json
from pathlib import Path
from typing import Any, List, Optional

from app.models.snapshot import Snapshot
from app.models.user import User

DEFAULT_IMPORT_DIR = Path("data/import")


def _parse_username(href: str) -> str:
    """Extract username from Instagram profile URL."""
    return href.rstrip("/").split("/")[-1]


def _decode_instagram_text(text: str) -> str:
    """Instagram exports UTF-8 strings as a sequence of byte code points."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _extract_from_label_values(label_values: List[dict[str, Any]]) -> dict[str, str]:
    """Extract username and full_name from Instagram label_values format."""
    result: dict[str, str] = {}
    for item in label_values:
        label = _decode_instagram_text(item.get("label", ""))
        value = _decode_instagram_text(item.get("value", ""))
        if label == "URL":
            result["url"] = value
        elif label in ("\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f", "Username"):
            result["username"] = value
        elif label in ("\u0418\u043c\u044f", "Name"):
            result["full_name"] = value
    return result


def _user_from_label_values(label_values: List[dict[str, Any]]) -> Optional[User]:
    data = _extract_from_label_values(label_values)
    username = data.get("username") or _parse_username(data.get("url", ""))
    if not username:
        return None
    return User(
        id=username,
        username=username,
        full_name=data.get("full_name", ""),
        is_private=False,
    )


class OfficialExportClient:
    def __init__(self, import_dir: Path = DEFAULT_IMPORT_DIR):
        self.import_dir = Path(import_dir)

    def login(self) -> None:
        pass

    def _find_file(self, pattern: str) -> Optional[Path]:
        matches = sorted(self.import_dir.glob(pattern))
        return matches[0] if matches else None

    def _read_followers(self) -> List[User]:
        path = self._find_file("followers_*.json")
        if not path:
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        users: List[User] = []
        for item in data:
            for entry in item.get("string_list_data", []):
                username = entry.get("value") or _parse_username(entry.get("href", ""))
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
        if not path:
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        users: List[User] = []
        for item in data.get("relationships_following", []):
            username = item.get("title", "")
            if not username and item.get("string_list_data"):
                username = _parse_username(item["string_list_data"][0].get("href", ""))
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

    def _read_label_value_users(self, pattern: str) -> List[User]:
        path = self._find_file(pattern)
        if not path:
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = [data]
        users: List[User] = []
        for item in data:
            user = _user_from_label_values(item.get("label_values", []))
            if user:
                users.append(user)
        return users

    def get_followers(self) -> List[User]:
        return self._read_followers()

    def get_following(self) -> List[User]:
        return self._read_following()

    def get_blocked(self) -> List[User]:
        return self._read_label_value_users("blocked_profiles.json")

    def get_hide_story_from(self) -> List[User]:
        return self._read_label_value_users("hide_story_from.json")

    def get_recently_unfollowed(self) -> List[User]:
        return self._read_label_value_users("recently_unfollowed_profiles.json")

    def get_recent_follow_requests(self) -> List[User]:
        return self._read_label_value_users("recent_follow_requests.json")

    def get_snapshot(self) -> Snapshot:
        return Snapshot(
            date=None,  # caller should set
            followers=self.get_followers(),
            following=self.get_following(),
            blocked=self.get_blocked(),
            hide_story_from=self.get_hide_story_from(),
            recently_unfollowed=self.get_recently_unfollowed(),
            recent_follow_requests=self.get_recent_follow_requests(),
        )
