from datetime import datetime

from twisted.trial.unittest import TestCase

from apns.utils import datetime_to_timestamp


class DatetimeToTimestampTestCase(TestCase):

    def test_datetime(self):
        now = datetime.now()

        timestamp = datetime_to_timestamp(now)

        self.assertEqual(datetime.fromtimestamp(timestamp),
                         now.replace(microsecond=0))
