from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from app.models.snapshot import Snapshot
from app.models.user import User
from app.repositories.json_repository import JsonRepository


def test_save_and_load_snapshot() -> None:
    with TemporaryDirectory() as tmp:
        repo = JsonRepository(Path(tmp))
        snapshot = Snapshot(
            date=date(2026, 7, 10),
            followers=[User(id="1", username="alice")],
            following=[User(id="2", username="bob")],
        )
        repo.save_snapshot(snapshot)
        loaded = repo.load_snapshot("2026-07-10")
        assert loaded is not None
        assert loaded.followers[0].username == "alice"


def test_latest_and_list() -> None:
    with TemporaryDirectory() as tmp:
        repo = JsonRepository(Path(tmp))
        repo.save_snapshot(Snapshot(
            date=date(2026, 7, 9),
            followers=[User(id="1", username="alice")],
            following=[User(id="2", username="bob")],
        ))
        repo.save_snapshot(Snapshot(
            date=date(2026, 7, 10),
            followers=[User(id="1", username="alice")],
            following=[User(id="2", username="bob")],
        ))
        latest = repo.get_latest_snapshot()
        assert latest is not None
        assert latest.date == date(2026, 7, 10)
        assert len(repo.list_snapshots()) == 2
