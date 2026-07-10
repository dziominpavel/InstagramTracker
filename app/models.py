from dataclasses import dataclass, field
from datetime import date
from typing import Any, List


@dataclass
class User:
    id: str
    username: str
    full_name: str = ""


@dataclass
class Snapshot:
    date: date
    followers: List[User]
    following: List[User]
    blocked: List[User] = field(default_factory=list)
    hide_story_from: List[User] = field(default_factory=list)
    recently_unfollowed: List[User] = field(default_factory=list)
    recent_follow_requests: List[User] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "followers": [u.__dict__ for u in self.followers],
            "following": [u.__dict__ for u in self.following],
            "blocked": [u.__dict__ for u in self.blocked],
            "hide_story_from": [u.__dict__ for u in self.hide_story_from],
            "recently_unfollowed": [u.__dict__ for u in self.recently_unfollowed],
            "recent_follow_requests": [u.__dict__ for u in self.recent_follow_requests],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snapshot":
        def _users(key: str) -> List[User]:
            return [User(**u) for u in data.get(key, [])]

        return cls(
            date=date.fromisoformat(data["date"]),
            followers=_users("followers"),
            following=_users("following"),
            blocked=_users("blocked"),
            hide_story_from=_users("hide_story_from"),
            recently_unfollowed=_users("recently_unfollowed"),
            recent_follow_requests=_users("recent_follow_requests"),
        )
