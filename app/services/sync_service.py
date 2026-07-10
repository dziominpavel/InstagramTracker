import logging
from datetime import date
from typing import Optional

from app.clients.instagram_client import InstagramClient
from app.models.snapshot import Snapshot
from app.repositories.json_repository import JsonRepository
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger("instagram_tracker")


class SyncService:
    def __init__(
        self,
        client: InstagramClient,
        repository: JsonRepository,
        target_username: str,
    ):
        self.client = client
        self.repository = repository
        self.target_username = target_username

    def run(
        self, snapshot_date: Optional[date] = None, source: str = "archive"
    ) -> Snapshot:
        logger.info("Reading followers")
        followers = self.client.get_followers()

        logger.info("Reading following")
        following = self.client.get_following()

        logger.info("Reading extra lists")
        blocked = self.client.get_blocked()
        hide_story_from = self.client.get_hide_story_from()
        recently_unfollowed = self.client.get_recently_unfollowed()
        recent_follow_requests = self.client.get_recent_follow_requests()

        snapshot = Snapshot(
            date=snapshot_date or date.today(),
            followers=followers,
            following=following,
            source=source,
            blocked=blocked,
            hide_story_from=hide_story_from,
            recently_unfollowed=recently_unfollowed,
            recent_follow_requests=recent_follow_requests,
        )

        prev = self.repository.get_latest_snapshot()

        logger.info("Saving snapshot for %s", snapshot.date.isoformat())
        self.repository.save_snapshot(snapshot)

        if prev and prev.date != snapshot.date:
            logger.info("Comparing with previous snapshot")
            AnalyticsService.diff(prev, snapshot)
        elif not prev:
            logger.info("No previous snapshot found, skipping comparison")
        else:
            logger.info("Previous snapshot is the same date, skipping comparison")

        logger.info("Done")
        return snapshot
