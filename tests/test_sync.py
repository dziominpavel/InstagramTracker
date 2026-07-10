from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from app.clients.mock_client import MockClient
from app.repositories.json_repository import JsonRepository
from app.services.sync_service import SyncService


def _fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def test_sync_pipeline() -> None:
    with TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        repo = JsonRepository(data_dir)

        client_09 = MockClient(
            _fixture_path("followers_09.json"),
            _fixture_path("following_09.json"),
        )
        service = SyncService(client_09, repo, "testuser")
        snapshot_09 = service.run(snapshot_date=date(2026, 7, 9), source="mock")
        assert snapshot_09.date == date(2026, 7, 9)
        assert len(snapshot_09.followers) == 3

        client_10 = MockClient(
            _fixture_path("followers_10.json"),
            _fixture_path("following_10.json"),
        )
        service = SyncService(client_10, repo, "testuser")
        snapshot_10 = service.run(snapshot_date=date(2026, 7, 10), source="mock")
        assert snapshot_10.date == date(2026, 7, 10)

        assert (data_dir / "snapshots" / "2026-07-09.json").exists()
        assert (data_dir / "snapshots" / "2026-07-10.json").exists()
