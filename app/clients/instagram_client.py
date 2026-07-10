from typing import List, Protocol

from app.models.user import User


class InstagramClient(Protocol):
    def login(self) -> None:
        ...

    def get_followers(self) -> List[User]:
        ...

    def get_following(self) -> List[User]:
        ...

    def get_blocked(self) -> List[User]:
        ...

    def get_hide_story_from(self) -> List[User]:
        ...

    def get_recently_unfollowed(self) -> List[User]:
        ...

    def get_recent_follow_requests(self) -> List[User]:
        ...
