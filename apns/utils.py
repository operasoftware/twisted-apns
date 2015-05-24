import time


def datetime_to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))
