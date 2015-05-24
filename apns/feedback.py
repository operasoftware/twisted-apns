from datetime import datetime
import binascii
import struct

from apns.utils import datetime_to_timestamp


class Feedback(object):
    FORMAT_PREFIX = '>IH'

    def __init__(self, when=None, token=None):
        self.when = when
        self.token = token

    def __str__(self):
        return '<Feedback: %s, %s>' % (self.token, self.when)


    @classmethod
    def from_binary_string(cls, stream):
        offset = 0
        length = len(stream)
        feedbacks = []

        while offset < length:
            timestamp, token_length = struct.unpack(cls.FORMAT_PREFIX,
                                                    stream[offset:offset+6])
            when = datetime.fromtimestamp(timestamp)
            offset += 6
            token = struct.unpack('>{0}s'.format(token_length),
                                  stream[offset:offset+token_length])[0]
            token = binascii.hexlify(token)
            offset += token_length
            feedbacks.append(cls(when, token))

        return feedbacks

    def to_binary_string(self):
        timestamp = datetime_to_timestamp(self.when)
        token = binascii.unhexlify(self.token)
        return struct.pack(self.FORMAT_PREFIX + '{0}s'.format(len(token)),
                           timestamp, len(token), token)


