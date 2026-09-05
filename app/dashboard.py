"""Shared dashboard payload + dual HTML generation (V1 + V2)."""
from pathlib import Path
from typing import Dict, List, Optional

from app import dashboard_v1, dashboard_v2
from app.models import Snapshot, User


def _users_payload(users: List[User], profiles: Optional[Dict[str, dict]] = None) -> List[Dict[str, str]]:
    result = []
    for u in users:
        entry = {"username": u.username, "full_name": u.full_name or ""}
        if profiles and u.username in profiles:
            p = profiles[u.username]
            if p.get("avatar_local"):
                entry["avatar_url"] = p["avatar_local"]
            elif p.get("avatar_url"):
                entry["avatar_url"] = p["avatar_url"]
            if p.get("full_name"):
                entry["full_name"] = p["full_name"]
            if p.get("followers_count"):
                entry["followers_count"] = p["followers_count"]
            if p.get("following_count"):
                entry["following_count"] = p["following_count"]
            if p.get("posts_count"):
                entry["posts_count"] = p["posts_count"]
            if p.get("status"):
                entry["status"] = p["status"]
        result.append(entry)
    return result


def build_payload(
    snapshot: Snapshot,
    all_snapshots: List[Snapshot],
    username: str,
    profiles: Optional[Dict[str, dict]] = None,
) -> dict:
    follower_ids = {u.id for u in snapshot.followers}
    following_ids = {u.id for u in snapshot.following}

    not_following_back = [u for u in snapshot.following if u.id not in follower_ids]
    fans = [u for u in snapshot.followers if u.id not in following_ids]
    mutual = [u for u in snapshot.followers if u.id in following_ids]
    # Pending requests only: export keeps accepted people in recent_follow_requests
    active_follow_requests = [
        u for u in snapshot.recent_follow_requests if u.username not in follower_ids
    ]

    snapshots_data = []
    for s in all_snapshots:
        if s.date == snapshot.date:
            continue
        snapshots_data.append({
            "date": s.date.isoformat(),
            "followers": _users_payload(s.followers, profiles),
            "following": _users_payload(s.following, profiles),
        })

    return {
        "username": username,
        "date": snapshot.date.isoformat(),
        "counts": {
            "followers": len(snapshot.followers),
            "following": len(snapshot.following),
            "mutual": len(mutual),
            "not_following_back": len(not_following_back),
            "fans": len(fans),
            "blocked": len(snapshot.blocked),
            "hide_story_from": len(snapshot.hide_story_from),
            "recent_follow_requests": len(active_follow_requests),
        },
        "lists": {
            "not_following_back": _users_payload(not_following_back, profiles),
            "fans": _users_payload(fans, profiles),
            "mutual": _users_payload(mutual, profiles),
            "followers": _users_payload(snapshot.followers, profiles),
            "following": _users_payload(snapshot.following, profiles),
            "blocked": _users_payload(snapshot.blocked, profiles),
            "hide_story_from": _users_payload(snapshot.hide_story_from, profiles),
            "recent_follow_requests": _users_payload(active_follow_requests, profiles),
        },
        "snapshots": snapshots_data,
    }


def save_dashboard(
    snapshot: Snapshot,
    all_snapshots: List[Snapshot],
    username: str,
    out: Path = Path("index.html"),
    profiles: Optional[Dict[str, dict]] = None,
) -> None:
    """Write V2 to ``out`` (default index.html) and V1 to index-v1.html beside it."""
    payload = build_payload(snapshot, all_snapshots, username, profiles)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dashboard_v2.render_html(payload), encoding="utf-8")
    v1_path = out.parent / "index-v1.html"
    v1_path.write_text(dashboard_v1.render_html(payload), encoding="utf-8")
