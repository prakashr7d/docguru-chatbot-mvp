import datetime
from datetime import datetime, timedelta  # noqa:  F811


def get_unblock_timestamp(after_n_minutes: int = 2) -> float:
    now = datetime.now()
    delta = timedelta(minutes=after_n_minutes)
    unblock_timestamp = now + delta
    print(type(unblock_timestamp))
    return unblock_timestamp
