import json
from pathlib import Path
from typing import Any, Dict


class SessionManager:
    def __init__(self, session_path: Path):
        self.session_path = Path(session_path)

    def load(self) -> Dict[str, Any]:
        if not self.session_path.exists():
            return {}
        return json.loads(self.session_path.read_text(encoding="utf-8"))

    def save(self, session: Dict[str, Any]) -> None:
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_path.write_text(
            json.dumps(session, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def is_valid(self) -> bool:
        session = self.load()
        return bool(session)
