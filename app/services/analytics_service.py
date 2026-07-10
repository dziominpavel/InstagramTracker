from typing import List

from app.models.event import Event
from app.models.snapshot import Snapshot
from app.models.user import User


class AnalyticsService:
    @staticmethod
    def not_following_back(snapshot: Snapshot) -> List[User]:
        follower_ids = snapshot.follower_ids
        return [u for u in snapshot.following if u.id not in follower_ids]

    @staticmethod
    def i_dont_follow_back(snapshot: Snapshot) -> List[User]:
        following_ids = snapshot.following_ids
        return [u for u in snapshot.followers if u.id not in following_ids]

    @staticmethod
    def mutual(snapshot: Snapshot) -> List[User]:
        follower_ids = snapshot.follower_ids
        return [u for u in snapshot.following if u.id in follower_ids]

    @staticmethod
    def diff(prev: Snapshot, curr: Snapshot) -> List[Event]:
        events: List[Event] = []

        prev_followers = {u.id: u for u in prev.followers}
        curr_followers = {u.id: u for u in curr.followers}
        prev_following = {u.id: u for u in prev.following}
        curr_following = {u.id: u for u in curr.following}

        # Followers changes
        for user_id, user in curr_followers.items():
            if user_id not in prev_followers:
                events.append(Event("FOLLOWED", curr.date.isoformat(), user))

        for user_id, user in prev_followers.items():
            if user_id not in curr_followers:
                events.append(Event("UNFOLLOWED", curr.date.isoformat(), user))

        # Following changes
        for user_id, user in curr_following.items():
            if user_id not in prev_following:
                events.append(Event("FOLLOWED_BY_ME", curr.date.isoformat(), user))

        for user_id, user in prev_following.items():
            if user_id not in curr_following:
                events.append(Event("UNFOLLOWED_BY_ME", curr.date.isoformat(), user))

        # Profile changes
        all_ids = (
            set(prev_followers)
            | set(curr_followers)
            | set(prev_following)
            | set(curr_following)
        )
        for user_id in all_ids:
            prev_user = prev_followers.get(user_id) or prev_following.get(user_id)
            curr_user = curr_followers.get(user_id) or curr_following.get(user_id)
            if not prev_user or not curr_user:
                continue

            if prev_user.username != curr_user.username:
                events.append(
                    Event(
                        "USERNAME_CHANGED",
                        curr.date.isoformat(),
                        curr_user,
                        prev_user.username,
                        curr_user.username,
                    )
                )

            if prev_user.full_name != curr_user.full_name:
                events.append(
                    Event(
                        "NAME_CHANGED",
                        curr.date.isoformat(),
                        curr_user,
                        prev_user.full_name,
                        curr_user.full_name,
                    )
                )

            if prev_user.is_private != curr_user.is_private:
                event_type = (
                    "BECAME_PRIVATE" if curr_user.is_private else "BECAME_PUBLIC"
                )
                events.append(
                    Event(
                        event_type,
                        curr.date.isoformat(),
                        curr_user,
                        str(prev_user.is_private),
                        str(curr_user.is_private),
                    )
                )

            if prev_user.profile_pic != curr_user.profile_pic:
                events.append(
                    Event(
                        "PROFILE_PHOTO_CHANGED",
                        curr.date.isoformat(),
                        curr_user,
                        prev_user.profile_pic,
                        curr_user.profile_pic,
                    )
                )

        return events
