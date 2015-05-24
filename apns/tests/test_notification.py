from datetime import datetime
import struct

from mock import patch
from twisted.trial.unittest import TestCase

from apns.notification import (
    Notification,
    NotificationInvalidCommandError,
    NotificationInvalidIdError,
    NotificationInvalidPriorityError,
    NotificationPayloadNotSerializableError,
    NotificationTokenUnhexlifyError
)


MODULE = 'apns.notification.'


class NotificationTestCase(TestCase):
    CLASS = MODULE + 'Notification.'

    @patch(CLASS + 'PRIORITIES', [0])
    def test_invalid_priority(self):
        notification = Notification()

        with self.assertRaises(NotificationInvalidPriorityError):
            notification.to_binary_string()

    @patch(CLASS + 'PRIORITIES', [0])
    def test_invalid_str(self):
        notification = Notification(None, 'token', None, 0)
        self.assertEqual(str(notification), '<Notification: token>')

    @patch(CLASS + 'PRIORITIES', [0])
    def test_to_binary_string_payload_not_json_serializable(self):
        notification = Notification(set(), '0000', None, 0)

        with self.assertRaises(NotificationPayloadNotSerializableError):
            notification.to_binary_string()

    @patch(CLASS + 'PRIORITIES', [0])
    def test_to_binary_string_token_unhexlify_error(self):
        notification = Notification('', '0', None, 0)

        with self.assertRaises(NotificationTokenUnhexlifyError) as ctx:
            notification.to_binary_string()

        self.assertEqual(str(ctx.exception), 'Odd-length string')

    @patch(CLASS + 'PRIORITIES', [0])
    def test_to_binary_string(self):
        notification = Notification('', '00', datetime.now(), 0)

        stream = notification.to_binary_string()

        notification.from_binary_string(stream)

    @patch(CLASS + 'PRIORITIES', [0])
    def test_from_binary_string_properties_set(self):
        now = datetime.now()
        stream = Notification('', '00', now, 0, 123).to_binary_string()
        notification = Notification()

        notification.from_binary_string(stream)

        self.assertEqual(notification.payload, '')
        self.assertEqual(notification.token, '00')
        self.assertEqual(notification.expire, now.replace(microsecond=0))
        self.assertEqual(notification.priority, 0)
        self.assertEqual(notification.iden, 123)

    @patch(CLASS + 'PRIORITIES', [0])
    def test_from_binary_string_invalid_command(self):
        notification = Notification('', '00', datetime.now(), 0)

        with self.assertRaises(NotificationInvalidCommandError):
            notification.from_binary_string(
                struct.pack('>B', notification.COMMAND + 1))

    @patch(CLASS + 'PRIORITIES', [0])
    def test_from_binary_string_invalid_id(self):
        now = datetime.now()
        stream = Notification('', '00', now, 0, 123).to_binary_string()
        notification = Notification()
        notification.EXPIRE = -1

        with self.assertRaises(NotificationInvalidIdError):
            notification.from_binary_string(stream)
