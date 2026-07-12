import json
import os
from datetime import date
from pathlib import Path
from typing import List, Optional

from app.models import Snapshot

SNAPSHOTS_DIR = Path("data/snapshots")


def _snapshot_path(snapshot_date: date) -> Path:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    return SNAPSHOTS_DIR / f"{snapshot_date.isoformat()}.json"


def save_snapshot(snapshot: Snapshot) -> None:
    path = _snapshot_path(snapshot.date)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(path))


def list_snapshots() -> List[Snapshot]:
    if not SNAPSHOTS_DIR.exists():
        return []
    snapshots = []
    for path in sorted(SNAPSHOTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshots.append(Snapshot.from_dict(data))
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return snapshots


def get_previous_snapshot(current_date: date) -> Optional[Snapshot]:
    snapshots = [s for s in list_snapshots() if s.date < current_date]
    return snapshots[-1] if snapshots else None


def load_snapshot(snapshot_date: date) -> Optional[Snapshot]:
    path = _snapshot_path(snapshot_date)
    if not path.exists():
        return None
    return Snapshot.from_dict(json.loads(path.read_text(encoding="utf-8")))
