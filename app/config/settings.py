import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    target_username: str
    session_path: str = "config/session.json"
    data_dir: str = "data"
    log_level: str = "INFO"
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None

    @classmethod
    def load(cls, path: Path = Path("config/config.json")) -> "Settings":
        load_dotenv()
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["instagram_username"] = os.getenv("INSTAGRAM_USERNAME")
        data["instagram_password"] = os.getenv("INSTAGRAM_PASSWORD")
        return cls(**data)

    def save(self, path: Path = Path("config/config.json")) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        public = {
            "target_username": self.target_username,
            "session_path": self.session_path,
            "data_dir": self.data_dir,
            "log_level": self.log_level,
        }
        path.write_text(
            json.dumps(public, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
