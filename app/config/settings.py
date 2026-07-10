import json
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    target_username: str
    data_dir: str = "data"
    log_level: str = "INFO"

    @classmethod
    def load(cls, path: Path = Path("config/config.json")) -> "Settings":
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, path: Path = Path("config/config.json")) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
