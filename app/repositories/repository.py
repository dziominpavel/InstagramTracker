from typing import List, Optional, Protocol

from app.models.snapshot import Snapshot


class Repository(Protocol):
    def save_snapshot(self, snapshot: Snapshot) -> None:
        ...

    def load_snapshot(self, date_str: str) -> Optional[Snapshot]:
        ...

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        ...

    def list_snapshots(self) -> List[Snapshot]:
        ...
