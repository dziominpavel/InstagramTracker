import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from app.models import Snapshot

PROFILES_PATH = Path("data/profiles.json")


def _load_cache() -> Dict[str, dict]:
    if PROFILES_PATH.exists():
        return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: Dict[str, dict]) -> None:
    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _extract_full_name(title: str) -> str:
    """Extract full name from og:title like 'Гильвей Юрий (@gilvei) • Instagram photos and videos'."""
    if not title:
        return ""
    # Remove ' • Instagram ...' suffix
    m = re.match(r"^(.*?)(?:\s*\(@[\w.]+\))?\s*•\s*Instagram", title)
    if m:
        return m.group(1).strip()
    return title.strip()


def _extract_stats(desc: str) -> dict:
    """Extract follower/following/post counts from og:description."""
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


def enrich_profiles(
    snapshot: Snapshot,
    delay: float = 2.0,
    limit: Optional[int] = None,
    force: bool = False,
) -> dict:
    """Fetch avatars and full names for all users in snapshot via Playwright."""
    from playwright.sync_api import sync_playwright

    cache = _load_cache()

    # Collect all unique usernames
    all_users: List[str] = []
    seen = set()
    for user in snapshot.followers + snapshot.following:
        if user.username not in seen:
            seen.add(user.username)
            all_users.append(user.username)

    # Filter: only fetch missing ones (unless force)
    to_fetch = all_users if force else [u for u in all_users if u not in cache]
    if limit:
        to_fetch = to_fetch[:limit]

    if not to_fetch:
        return {"total": len(all_users), "fetched": 0, "skipped": len(all_users), "failed": 0}

    print(f"Total users: {len(all_users)}, to fetch: {len(to_fetch)}")

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
            url = f"https://www.instagram.com/{username}/"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)

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

                full_name = _extract_full_name(title or "")
                stats = _extract_stats(desc or "")

                cache[username] = {
                    "username": username,
                    "full_name": full_name,
                    "avatar_url": pic or "",
                    "followers_count": stats.get("followers_count"),
                    "following_count": stats.get("following_count"),
                    "posts_count": stats.get("posts_count"),
                }
                fetched += 1
                status = "OK" if pic else "no-pic"
                print(f"  [{i+1}/{len(to_fetch)}] @{username}: {status} | {full_name[:30]}")

            except Exception as e:
                failed += 1
                cache[username] = {"username": username, "full_name": "", "avatar_url": "", "error": str(e)[:100]}
                print(f"  [{i+1}/{len(to_fetch)}] @{username}: ERROR {e}")

            # Save cache every 10 profiles
            if (i + 1) % 10 == 0:
                _save_cache(cache)

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
