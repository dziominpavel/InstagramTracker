import json
import re
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.models import Snapshot

PROFILES_PATH = Path("data/profiles.json")
AVATARS_DIR = Path("data/avatars")
METADATA_CACHE_DAYS = 30   # re-fetch name/stats if older than this
AVATAR_CACHE_DAYS = 90     # re-download avatar image if older than this


def _load_cache() -> Dict[str, dict]:
    if PROFILES_PATH.exists():
        return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: Dict[str, dict]) -> None:
    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _avatar_path(username: str) -> Path:
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)
    return AVATARS_DIR / f"{username}.jpg"


def _extract_full_name(title: str) -> str:
    if not title:
        return ""
    m = re.match(r"^(.*?)(?:\s*\(@[\w.]+\))?\s*•\s*Instagram", title)
    if m:
        return m.group(1).strip()
    return title.strip()


def _extract_stats(desc: str) -> dict:
    if not desc:
        return {}
    followers = re.search(r"([\d,.]+)\s*Followers?", desc)
    following = re.search(r"([\d,.]+)\s*Following?", desc)
    posts = re.search(r"([\d,.]+)\s*Posts?", desc)
    return {
        "followers_count": followers.group(1).replace(",", "") if followers else None,
        "following_count": following.group(1).replace(",", "") if following else None,
        "posts_count": posts.group(1).replace(",", "") if posts else None,
    }


def _age_days(entry: dict) -> int:
    """How many days since this profile was cached."""
    cached_date = entry.get("cached_at")
    if not cached_date:
        return 9999
    try:
        d = datetime.fromisoformat(cached_date).date()
        return (date.today() - d).days
    except (ValueError, TypeError):
        return 9999


def _needs_fetch(username: str, cache: Dict[str, dict]) -> bool:
    """Check if we need to fetch this profile."""
    entry = cache.get(username)
    if not entry:
        return True  # not in cache at all

    # Profiles with errors (login_wall, timeout) — retry every time
    if entry.get("error"):
        return True

    age = _age_days(entry)

    # Metadata (name, stats) — refresh after METADATA_CACHE_DAYS
    if age >= METADATA_CACHE_DAYS:
        return True

    # Avatar file missing — need to download
    if entry.get("avatar_local") and not _avatar_path(username).exists():
        return True

    # Avatar itself — refresh after AVATAR_CACHE_DAYS
    if age >= AVATAR_CACHE_DAYS:
        return True

    return False


def _download_avatar(url: str, username: str) -> bool:
    """Download avatar image to local file (basic urllib, may fail without session)."""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read()
        if len(data) < 100:
            return False
        # Verify it's actually an image
        if data[:2] != b"\xff\xd8" and data[:4] != b"\x89PNG":  # not JPEG or PNG
            return False
        _avatar_path(username).write_bytes(data)
        return True
    except Exception:
        return False


def _download_avatar_via_page(page, url: str, username: str) -> bool:
    """Download avatar image using Playwright page context (has session cookies)."""
    if not url:
        return False
    try:
        resp = page.request.get(url, timeout=15000)
        if resp.status != 200:
            return False
        data = resp.body()
        if len(data) < 100:
            return False
        # Verify it's actually an image
        if data[:2] != b"\xff\xd8" and data[:4] != b"\x89PNG":
            return False
        _avatar_path(username).write_bytes(data)
        return True
    except Exception:
        return False


def _fetch_single(page, username: str, cache_entry: dict = None) -> dict:
    """Fetch a single profile via Playwright page object."""
    url = f"https://www.instagram.com/{username}/"
    page.goto(url, wait_until="networkidle", timeout=25000)
    page.wait_for_timeout(2000)

    pic = page.evaluate('''
        () => {
            const m = document.querySelector('meta[property="og:image"]');
            return m ? m.content : null;
        }
    ''')
    title = page.evaluate('''
        () => {
            const m = document.querySelector('meta[property="og:title"]');
            return m ? m.content : null;
        }
    ''')
    desc = page.evaluate('''
        () => {
            const m = document.querySelector('meta[property="og:description"]');
            return m ? m.content : null;
        }
    ''')

    # Detect login wall: og:title is just "Instagram" without username
    if not title or (username not in (title or "") and "Instagram" in (title or "") and "@" not in (title or "")):
        return {
            "username": username,
            "full_name": "",
            "avatar_url": "",
            "avatar_local": "",
            "cached_at": date.today().isoformat(),
            "error": "login_wall",
        }

    full_name = _extract_full_name(title or "")
    stats = _extract_stats(desc or "")

    # Download avatar image locally (via Playwright session)
    # Only re-download if avatar file doesn't exist or is older than AVATAR_CACHE_DAYS
    avatar_downloaded = False
    avatar_file = _avatar_path(username)
    cached_age = _age_days(cache_entry) if cache_entry else 9999
    need_avatar_download = (not avatar_file.exists()) or (cached_age >= AVATAR_CACHE_DAYS)
    if pic and need_avatar_download:
        avatar_downloaded = _download_avatar_via_page(page, pic, username)
    elif avatar_file.exists():
        avatar_downloaded = True  # keep existing file

    return {
        "username": username,
        "full_name": full_name,
        "avatar_url": pic or "",
        "avatar_local": f"data/avatars/{username}.jpg" if (avatar_downloaded or avatar_file.exists()) else "",
        "followers_count": stats.get("followers_count"),
        "following_count": stats.get("following_count"),
        "posts_count": stats.get("posts_count"),
        "cached_at": date.today().isoformat(),
    }


def enrich_profiles(
    snapshot: Snapshot,
    delay: float = 2.0,
    limit: Optional[int] = None,
    force: bool = False,
    on_progress: Optional[callable] = None,
) -> dict:
    """Fetch avatars and full names for users in snapshot via Playwright."""
    from playwright.sync_api import sync_playwright

    cache = _load_cache()

    # Collect all unique usernames
    all_users: List[str] = []
    seen: Set[str] = set()
    for user in snapshot.followers + snapshot.following:
        if user.username not in seen:
            seen.add(user.username)
            all_users.append(user.username)

    # Determine which need fetching
    if force:
        to_fetch = all_users
    else:
        to_fetch = [u for u in all_users if _needs_fetch(u, cache)]
    if limit:
        to_fetch = to_fetch[:limit]

    if not to_fetch:
        return {"total": len(all_users), "fetched": 0, "skipped": len(all_users), "failed": 0}

    print(f"Avatars to fetch: {len(to_fetch)} out of {len(all_users)}", flush=True)

    fetched = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        for i, username in enumerate(to_fetch):
            try:
                result = _fetch_single(page, username, cache.get(username))
                cache[username] = result
                fetched += 1
                status = "OK" if result.get("avatar_local") else "no-pic"
                print(f"  [{i+1}/{len(to_fetch)}] @{username}: {status}", flush=True)
            except Exception as e:
                failed += 1
                cache[username] = {
                    "username": username,
                    "full_name": "",
                    "avatar_url": "",
                    "avatar_local": "",
                    "cached_at": date.today().isoformat(),
                    "error": str(e)[:100],
                }
                print(f"  [{i+1}/{len(to_fetch)}] @{username}: ERROR {e}", flush=True)

            # Save cache every 10 profiles and regenerate dashboard
            if (i + 1) % 10 == 0:
                _save_cache(cache)
                if on_progress:
                    try:
                        on_progress(i + 1, len(to_fetch))
                    except Exception:
                        pass

            time.sleep(delay)

        browser.close()

    _save_cache(cache)

    return {
        "total": len(all_users),
        "fetched": fetched,
        "skipped": len(all_users) - len(to_fetch),
        "failed": failed,
    }


def get_profiles() -> Dict[str, dict]:
    """Load cached profile data (avatars, names, stats)."""
    return _load_cache()


def get_stale_count(snapshot: Snapshot) -> int:
    """Count how many profiles need fetching (for info message)."""
    cache = _load_cache()
    all_users = {u.username for u in snapshot.followers + snapshot.following}
    return sum(1 for u in all_users if _needs_fetch(u, cache))
