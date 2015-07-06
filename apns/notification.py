from datetime import datetime
import binascii
import json
import struct

from apns.commands import NOTIFICATION
from apns.utils import datetime_to_timestamp


class NotificationError(Exception):
    """To be thrown upon failures on notification processing."""
    pass


class NotificationInvalidPriorityError(NotificationError):
    """
    Thrown while packing a notification, if the notification priority field is
    invalid.
    """
    pass


class NotificationPayloadNotSerializableError(NotificationError):
    """
    Thrown while packing a notification, if the notification payload field
    could not be serialized to JSON.
    """
    pass


class NotificationTokenUnhexlifyError(NotificationError):
    """
    Thrown while packing a notification, if the notification token field could
    not be converted to binary from its hex representation.
    """
    def __init__(self, msg):
        super(NotificationTokenUnhexlifyError, self).__init__(msg)


class NotificationInvalidCommandError(NotificationError):
    """
    Thrown while unpacking a notification, if the notification command field
    contains invalid value.
    """
    pass


class NotificationInvalidIdError(NotificationError):
    """
    Thrown while unpacking a notification, if the notification structure is
    invalid.
    """
    pass


class Notification(object):
    """
    A representation of the structure of a notification request, as defined in
    the iOS documentation.
    """
    COMMAND = NOTIFICATION
    PRIORITY_NORMAL = 5
    PRIORITY_IMMEDIATELY = 10

    PRIORITIES = (PRIORITY_NORMAL, PRIORITY_IMMEDIATELY)

    PAYLOAD = 2
    TOKEN = 1
    PRIORITY = 5
    NOTIFICATION_ID = 3
    EXPIRE = 4

    EXPIRE_IMMEDIATELY = 0

    def __init__(self, payload=None, token=None, expire=None,
                 priority=PRIORITY_NORMAL, iden=0):
        """
        Init an instance of Notification.
        :param payload: object containing structure of payload to be sent to
        remote device.
        :param token: string containing target device token in hex
        :param expire: notification expire time as UNIX timestamp, 0 means that
        notification expires immediately.
        :param priority: notification priority, as described in iOS
        documentation
        :param iden: notification ID, as described in iOS documentation
        """
        self.payload = payload
        self.token = token
        self.expire = expire
        self.priority = priority
        self.iden = iden

    def __str__(self):
        return '<Notification: %s>' % self.token

    def to_binary_string(self):
        """Pack the notification to binary form and return it as string."""
        if self.priority not in self.PRIORITIES:
            raise NotificationInvalidPriorityError()

        try:
            token = binascii.unhexlify(self.token)
        except TypeError as error:
            raise NotificationTokenUnhexlifyError(error)

        try:
            payload = json.dumps(self.payload)
        except TypeError:
            raise NotificationPayloadNotSerializableError()

        fmt = ">BIBH{0}sBH{1}sBHIBHIBHB".format(len(token), len(payload))

        expire = (0 if self.expire == self.EXPIRE_IMMEDIATELY else
                  datetime_to_timestamp(self.expire))

        # |COMMAND|FRAME-LEN|{token}|{payload}|{id:4}|{expire:4}|{priority:1}
        # 5 items, each 3 bytes prefix, then each item length
        length = 3*5 + len(token) + len(payload) + 4 + 4 + 1
        message = struct.pack(fmt, self.COMMAND, length,
                              self.TOKEN, len(token), token,
                              self.PAYLOAD, len(payload), payload,
                              self.NOTIFICATION_ID, 4, self.iden,
                              self.EXPIRE, 4, expire,
                              self.PRIORITY, 1, self.priority)
        return message

    def from_binary_string(self, notification):
        """Unpack the notification from binary string."""
        command = struct.unpack('>B', notification[0])[0]

        if command != self.COMMAND:
            raise NotificationInvalidCommandError()

        length = struct.unpack('>I', notification[1:5])[0]
        notification = notification[5:]
        offset = 0

        def next_item(offset):
            iden, length = struct.unpack('>BH', notification[offset:offset+3])
            offset += 3
            payload = notification[offset:offset+length]
            offset += length

            if iden == self.PAYLOAD:
                payload = struct.unpack('>{0}s'.format(length), payload)[0]
                self.payload = json.loads(payload)
            elif iden == self.TOKEN:
                payload = struct.unpack('>{0}s'.format(length), payload)[0]
                self.token = binascii.hexlify(payload)
            elif iden == self.PRIORITY:
                self.priority = struct.unpack('>B', payload)[0]
            elif iden == self.NOTIFICATION_ID:
                self.iden = struct.unpack('>I', payload)[0]
            elif iden == self.EXPIRE:
                payload = struct.unpack('>I', payload)[0]
                self.expire = (self.EXPIRE_IMMEDIATELY if payload == 0 else
                               datetime.fromtimestamp(payload))
            else:
                raise NotificationInvalidIdError()

            return offset

        while offset < length:
            offset = next_item(offset)
