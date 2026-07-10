import json
from pathlib import Path
from typing import List

from app.models.event import Event
from app.models.snapshot import Snapshot


class ReportService:
    def __init__(self, data_dir: Path):
        self.reports_dir = Path(data_dir) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: Snapshot, events: List[Event]) -> Path:
        report = {
            "date": snapshot.date.isoformat(),
            "followers_count": len(snapshot.followers),
            "following_count": len(snapshot.following),
            "events": [event.to_dict() for event in events],
        }
        path = self.reports_dir / f"{snapshot.date.isoformat()}.json"
        path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def load(self, date_str: str) -> dict:
        path = self.reports_dir / f"{date_str}.json"
        if not path.exists():
            raise FileNotFoundError(f"Report not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
