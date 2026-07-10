from dataclasses import dataclass, field
from datetime import date
from typing import Any, List

from .user import User


@dataclass
class Snapshot:
    date: date
    followers: List[User]
    following: List[User]
    source: str = "official_export"
    blocked: List[User] = field(default_factory=list)
    hide_story_from: List[User] = field(default_factory=list)
    recently_unfollowed: List[User] = field(default_factory=list)
    recent_follow_requests: List[User] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "followers": [u.to_dict() for u in self.followers],
            "following": [u.to_dict() for u in self.following],
            "source": self.source,
            "blocked": [u.to_dict() for u in self.blocked],
            "hide_story_from": [u.to_dict() for u in self.hide_story_from],
            "recently_unfollowed": [u.to_dict() for u in self.recently_unfollowed],
            "recent_follow_requests": [u.to_dict() for u in self.recent_follow_requests],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snapshot":
        return cls(
            date=date.fromisoformat(data["date"]),
            followers=[User.from_dict(u) for u in data.get("followers", [])],
            following=[User.from_dict(u) for u in data.get("following", [])],
            source=data.get("source", "official_export"),
            blocked=[User.from_dict(u) for u in data.get("blocked", [])],
            hide_story_from=[User.from_dict(u) for u in data.get("hide_story_from", [])],
            recently_unfollowed=[User.from_dict(u) for u in data.get("recently_unfollowed", [])],
            recent_follow_requests=[User.from_dict(u) for u in data.get("recent_follow_requests", [])],
        )

    @property
    def follower_ids(self) -> set[str]:
        return {u.id for u in self.followers}

    @property
    def following_ids(self) -> set[str]:
        return {u.id for u in self.following}
