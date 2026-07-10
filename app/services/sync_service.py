import logging
from datetime import date
from typing import Optional

from app.clients.instagram_client import InstagramClient
from app.models.snapshot import Snapshot
from app.repositories.json_repository import JsonRepository
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

logger = logging.getLogger("instagram_tracker")


class SyncService:
    def __init__(
        self,
        client: InstagramClient,
        repository: JsonRepository,
        report_service: ReportService,
        target_username: str,
    ):
        self.client = client
        self.repository = repository
        self.report_service = report_service
        self.target_username = target_username

    def run(
        self, snapshot_date: Optional[date] = None, source: str = "archive"
    ) -> Snapshot:
        logger.info("Logging in")
        self.client.login()

        logger.info("Downloading followers")
        followers = self.client.get_followers()

        logger.info("Downloading following")
        following = self.client.get_following()

        snapshot = Snapshot(
            date=snapshot_date or date.today(),
            followers=followers,
            following=following,
            source=source,
        )

        prev = self.repository.get_latest_snapshot()

        logger.info("Saving snapshot for %s", snapshot.date.isoformat())
        self.repository.save_snapshot(snapshot)

        if prev and prev.date != snapshot.date:
            logger.info("Comparing with previous snapshot")
            events = AnalyticsService.diff(prev, snapshot)
            logger.info("Saving report")
            self.report_service.save(snapshot, events)
        elif not prev:
            logger.info("No previous snapshot found, skipping comparison")
        else:
            logger.info("Previous snapshot is the same date, skipping comparison")

        logger.info("Done")
        return snapshot
