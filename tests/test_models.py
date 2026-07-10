from datetime import date

from app.models.snapshot import Snapshot
from app.models.user import User


def test_user_from_dict() -> None:
    user = User.from_dict({
        "id": 123,
        "username": "alice",
        "full_name": "Alice",
        "is_private": True,
        "profile_pic": "http://example.com/pic.jpg",
    })
    assert user.id == "123"
    assert user.username == "alice"
    assert user.is_private is True


def test_snapshot_roundtrip() -> None:
    snapshot = Snapshot(
        date=date(2026, 7, 10),
        followers=[User(id="1", username="alice")],
        following=[User(id="2", username="bob")],
        source="mock",
    )
    data = snapshot.to_dict()
    restored = Snapshot.from_dict(data)
    assert restored.date == date(2026, 7, 10)
    assert restored.followers[0].username == "alice"
    assert restored.following[0].username == "bob"
    assert restored.source == "mock"
