import time


def datetime_to_timestamp(dt):
    """Produce UNIX timestamp from specified date."""
    return int(time.mktime(dt.timetuple()))
