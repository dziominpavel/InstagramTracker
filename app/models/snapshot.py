from dataclasses import dataclass, field
from datetime import date
from typing import Any, List

from .user import User


@dataclass
class Snapshot:
    date: date
    followers: List[User]
    following: List[User]
    source: str = "archive"

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "followers": [u.to_dict() for u in self.followers],
            "following": [u.to_dict() for u in self.following],
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snapshot":
        return cls(
            date=date.fromisoformat(data["date"]),
            followers=[User.from_dict(u) for u in data.get("followers", [])],
            following=[User.from_dict(u) for u in data.get("following", [])],
            source=data.get("source", "archive"),
        )

    @property
    def follower_ids(self) -> set[str]:
        return {u.id for u in self.followers}

    @property
    def following_ids(self) -> set[str]:
        return {u.id for u in self.following}
