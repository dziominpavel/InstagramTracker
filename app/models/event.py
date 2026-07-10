from dataclasses import dataclass
from typing import Any, Optional

from .user import User


@dataclass
class Event:
    event_type: str
    date: str
    user: User
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "date": self.date,
            "user": self.user.to_dict(),
            "old_value": self.old_value,
            "new_value": self.new_value,
        }
