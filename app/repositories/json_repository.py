import json
from pathlib import Path
from typing import List, Optional

from app.models.snapshot import Snapshot


class JsonRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.snapshots_dir = self.data_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, date_str: str) -> Path:
        return self.snapshots_dir / f"{date_str}.json"

    def save_snapshot(self, snapshot: Snapshot) -> None:
        path = self._snapshot_path(snapshot.date.isoformat())
        path.write_text(
            json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_snapshot(self, date_str: str) -> Optional[Snapshot]:
        path = self._snapshot_path(date_str)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Snapshot.from_dict(data)

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        snapshots = self.list_snapshots()
        if not snapshots:
            return None
        return max(snapshots, key=lambda s: s.date)

    def list_snapshots(self) -> List[Snapshot]:
        snapshots = []
        for path in sorted(self.snapshots_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshots.append(Snapshot.from_dict(data))
        return snapshots
