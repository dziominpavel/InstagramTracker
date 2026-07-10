from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class User:
    id: str
    username: str
    full_name: str = ""
    is_private: bool = False
    profile_pic: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "is_private": self.is_private,
            "profile_pic": self.profile_pic,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(
            id=str(data["id"]),
            username=data.get("username", ""),
            full_name=data.get("full_name", ""),
            is_private=data.get("is_private", False),
            profile_pic=data.get("profile_pic"),
        )
