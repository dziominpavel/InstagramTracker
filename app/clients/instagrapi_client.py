from typing import List

from app.models.user import User
from app.session.session_manager import SessionManager


class InstagrapiClient:
    def __init__(
        self,
        username: str,
        password: str,
        target_username: str,
        session_manager: SessionManager,
    ):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.session_manager = session_manager

    def login(self) -> None:
        raise NotImplementedError("InstagrapiClient is not implemented yet")

    def get_followers(self) -> List[User]:
        raise NotImplementedError("InstagrapiClient is not implemented yet")

    def get_following(self) -> List[User]:
        raise NotImplementedError("InstagrapiClient is not implemented yet")
