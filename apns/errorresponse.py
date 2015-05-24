import struct

from apns.commands import ERROR_RESPONSE


class ErrorResponseError(Exception):
    pass


class ErrorResponseInvalidCommandError(ErrorResponseError):
    pass


class ErrorResponseInvalidCodeError(ErrorResponseError):
    pass


class ErrorResponse(object):
    CODES = {
        0: 'No errors encountered',
        1: 'Processing error',
        2: 'Missing device token',
        3: 'Missing topic',
        4: 'Missing payload',
        5: 'Invalid token size',
        6: 'Invalid topic size',
        7: 'Invalid payload size',
        8: 'Invalid token',
        10: 'Shutdown',
        255: 'Unknown'
    }

    FORMAT = '>BBI'
    COMMAND = ERROR_RESPONSE

    def __init__(self):
        self.code = self.name = self.identifier = None

    def __str__(self):
        return '<ErrorResponse: %s>' % self.name

    def from_binary_string(self, stream):
        command, code, identifier = struct.unpack(self.FORMAT, stream)

        if command != self.COMMAND:
            raise ErrorResponseInvalidCommandError()

        if code not in self.CODES:
            raise ErrorResponseInvalidCodeError()

        self.code = code
        self.name = self.CODES[code]
        self.identifier = identifier

    def to_binary_string(self, code, identifier):
        return struct.pack(self.FORMAT, self.COMMAND, code, identifier)
