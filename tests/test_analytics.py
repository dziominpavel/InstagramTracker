from datetime import date

from app.models.snapshot import Snapshot
from app.models.user import User
from app.services.analytics_service import AnalyticsService


def _make_snapshot(day: int) -> Snapshot:
    return Snapshot(
        date=date(2026, 7, day),
        followers=[
            User(id="1", username="alice"),
            User(id="2", username="bob"),
        ],
        following=[
            User(id="1", username="alice"),
            User(id="3", username="charlie"),
        ],
    )


def test_not_following_back() -> None:
    snapshot = _make_snapshot(10)
    result = AnalyticsService.not_following_back(snapshot)
    assert len(result) == 1
    assert result[0].username == "charlie"


def test_i_dont_follow_back() -> None:
    snapshot = _make_snapshot(10)
    result = AnalyticsService.i_dont_follow_back(snapshot)
    assert len(result) == 1
    assert result[0].username == "bob"


def test_mutual() -> None:
    snapshot = _make_snapshot(10)
    result = AnalyticsService.mutual(snapshot)
    assert len(result) == 1
    assert result[0].username == "alice"


def test_diff() -> None:
    prev = Snapshot(
        date=date(2026, 7, 9),
        followers=[User(id="1", username="alice")],
        following=[User(id="2", username="bob")],
    )
    curr = Snapshot(
        date=date(2026, 7, 10),
        followers=[User(id="1", username="alice"), User(id="3", username="charlie")],
        following=[User(id="2", username="bob_new")],
    )
    events = AnalyticsService.diff(prev, curr)
    types = {e.event_type for e in events}
    assert "FOLLOWED" in types
    assert "USERNAME_CHANGED" in types
