import logging
from typing import List

from instagrapi import Client

from app.models.user import User
from app.session.session_manager import SessionManager

logger = logging.getLogger("instagram_tracker")


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
        self._client = Client()

    def login(self) -> None:
        session = self.session_manager.load()
        if session:
            try:
                self._client.load_settings(session)
                self._client.login(self.username, self.password)
                logger.info("Logged in using existing session")
                return
            except Exception as exc:
                logger.warning("Failed to use saved session: %s", exc)

        if not self.username or not self.password:
            raise ValueError("Instagram username and password are required")

        self._client.login(self.username, self.password)
        self.session_manager.save(self._client.dump_settings())
        logger.info("Logged in with fresh credentials")

    def _user_to_model(self, user) -> User:
        return User(
            id=str(user.pk),
            username=user.username,
            full_name=user.full_name or "",
            is_private=getattr(user, "is_private", False),
            profile_pic=getattr(user, "profile_pic_url", None),
        )

    def _get_user_id(self) -> int:
        user_id = self._client.user_id_from_username(self.target_username)
        if not user_id:
            raise ValueError(f"User not found: {self.target_username}")
        return user_id

    def get_followers(self) -> List[User]:
        user_id = self._get_user_id()
        followers = self._client.user_followers(user_id)
        return [self._user_to_model(u) for u in followers.values()]

    def get_following(self) -> List[User]:
        user_id = self._get_user_id()
        following = self._client.user_following(user_id)
        return [self._user_to_model(u) for u in following.values()]
