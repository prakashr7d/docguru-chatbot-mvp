import datetime
from datetime import datetime, timedelta  # noqa:  F811


def get_unblock_timestamp(after_n_minutes: int = 2) -> datetime:
    now = datetime.now()
    delta = timedelta(minutes=after_n_minutes)
    unblock_timestamp = now + delta
    return unblock_timestamp


def get_feedback_timestamp(after_n_minutes: int = 2) -> datetime:
    now = datetime.now()
    delta = timedelta(seconds=after_n_minutes)
    feedback_timestamp = now + delta
    return feedback_timestamp

