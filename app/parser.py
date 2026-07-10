import json
from pathlib import Path
from typing import Any, List, Optional

from app.models import Snapshot, User


def _decode_instagram_text(text: str) -> str:
    """Instagram exports UTF-8 strings as a sequence of byte code points."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _parse_username(href: str) -> str:
    return href.rstrip("/").split("/")[-1]


def _extract_from_label_values(label_values: List[dict[str, Any]]) -> dict[str, str]:
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
    return User(id=username, username=username, full_name=data.get("full_name", ""))


class ExportParser:
    def __init__(self, import_dir: Path = Path("data/import")):
        self.import_dir = Path(import_dir)

    def _find_files(self, pattern: str) -> List[Path]:
        return sorted(self.import_dir.glob(pattern))

    def _read_json(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_followers(self) -> List[User]:
        users: List[User] = []
        for path in self._find_files("followers_*.json"):
            for item in self._read_json(path):
                for entry in item.get("string_list_data", []):
                    username = entry.get("value") or _parse_username(entry.get("href", ""))
                    if username:
                        users.append(User(id=username, username=username))
        return users

    def _read_following(self) -> List[User]:
        path = self._find_files("following.json")
        if not path:
            return []
        users: List[User] = []
        for item in self._read_json(path[0]).get("relationships_following", []):
            username = item.get("title", "")
            if not username and item.get("string_list_data"):
                username = _parse_username(item["string_list_data"][0].get("href", ""))
            if username:
                users.append(User(id=username, username=username))
        return users

    def _read_label_value_users(self, pattern: str) -> List[User]:
        paths = self._find_files(pattern)
        if not paths:
            return []
        users: List[User] = []
        for path in paths:
            data = self._read_json(path)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                user = _user_from_label_values(item.get("label_values", []))
                if user:
                    users.append(user)
        return users

    def parse(self) -> Snapshot:
        return Snapshot(
            date=None,  # set by caller
            followers=self._read_followers(),
            following=self._read_following(),
            blocked=self._read_label_value_users("blocked_profiles.json"),
            hide_story_from=self._read_label_value_users("hide_story_from.json"),
            recently_unfollowed=self._read_label_value_users("recently_unfollowed_profiles.json"),
            recent_follow_requests=self._read_label_value_users("recent_follow_requests.json"),
        )
