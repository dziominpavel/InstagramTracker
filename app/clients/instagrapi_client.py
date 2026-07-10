import logging
from typing import Callable, List, Optional

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

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
        code_callback: Optional[Callable[[str], str]] = None,
    ):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.session_manager = session_manager
        self.code_callback = code_callback or (lambda msg: input(msg))
        self._client = Client()
        self._session_path = str(self.session_manager.session_path)

    def _save_session(self) -> None:
        """Persist instagrapi session settings to disk."""
        self.session_manager.session_path.parent.mkdir(parents=True, exist_ok=True)
        self._client.dump_settings(self._session_path)

    def _load_session(self) -> bool:
        """Load session settings from disk if they exist."""
        if not self.session_manager.session_path.exists():
            return False
        try:
            self._client.load_settings(self._session_path)
            return True
        except Exception as exc:
            logger.warning("Failed to load saved session: %s", exc)
            return False

    def _try_login(self, verification_code: str = "") -> bool:
        """Attempt to login. Returns True on success."""
        try:
            self._client.login(
                self.username, self.password, verification_code=verification_code
            )
            return True
        except TwoFactorRequired:
            raise
        except ChallengeRequired:
            self._save_session()
            raise

    def login(self) -> None:
        if self._load_session():
            if self._client.user_id:
                logger.info("Logged in using existing session")
                return
            try:
                if self._try_login():
                    self._save_session()
                    logger.info("Logged in using existing session")
                    return
            except TwoFactorRequired:
                pass  # will handle below
            except ChallengeRequired as exc:
                self._handle_challenge(exc)
                return

        if not self.username or not self.password:
            raise ValueError("Instagram username and password are required")

        try:
            if self._try_login():
                self._save_session()
                logger.info("Logged in with fresh credentials")
                return
        except TwoFactorRequired:
            code = self.code_callback(
                "Enter Instagram 2FA verification code (6 digits): "
            )
            if self._try_login(verification_code=code):
                self._save_session()
                logger.info("Logged in with 2FA code")
                return
        except ChallengeRequired as exc:
            self._handle_challenge(exc)

    def _handle_challenge(self, exc: ChallengeRequired) -> None:
        """Handle Instagram challenge. Native flow requires manual confirmation."""
        challenge = getattr(exc, "challenge", None) or {}
        if challenge.get("native_flow"):
            raise RuntimeError(
                "Instagram requires manual confirmation. "
                "Open the Instagram app or website, approve the login attempt, "
                "then run login.bat again."
            )
        code = self.code_callback("Enter Instagram challenge code (6 digits): ")
        try:
            self._client.challenge_code_handler(self.username, choice=None)
        except Exception:
            pass
        if self._client.login(self.username, self.password, verification_code=code):
            self._save_session()
            logger.info("Logged in after challenge")
            return
        raise RuntimeError(
            "Could not resolve Instagram challenge. "
            "Please approve the login in the Instagram app and try again."
        )

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
