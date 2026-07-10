from typing import List, Protocol

from app.models.user import User


class InstagramClient(Protocol):
    def login(self) -> None:
        ...

    def get_followers(self) -> List[User]:
        ...

    def get_following(self) -> List[User]:
        ...
