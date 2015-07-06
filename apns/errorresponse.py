import struct

from apns.commands import ERROR_RESPONSE


class ErrorResponseError(Exception):
    """To be thrown upon failures on error response processing."""
    pass


class ErrorResponseInvalidCommandError(ErrorResponseError):
    """
    Thrown while unpacking an error response, if the command field contains
    invalid value.
    """
    pass


class ErrorResponseInvalidCodeError(ErrorResponseError):
    """
    Thrown while unpacking an error response, if the status code field contains
    invalid value.
    """
    pass


class ErrorResponse(object):
    """
    A representation of the structure of an error response, as defined in the
    iOS documentation.
    """
    CODE_OK = 0
    CODE_PROCESSING_ERROR = 1
    CODE_MISSING_TOKEN = 2
    CODE_MISSING_TOPIC = 3
    CODE_MISSING_PAYLOAD = 4
    CODE_INVALID_TOKEN_SIZE = 5
    CODE_INVALID_TOPIC_SIZE = 6
    CODE_INVALID_PAYLOAD_SIZE = 7
    CODE_INVALID_TOKEN = 8
    CODE_SHUTDOWN = 10
    CODE_UNKNOWN = 255

    CODES = {
        CODE_OK: 'No errors encountered',
        CODE_PROCESSING_ERROR: 'Processing error',
        CODE_MISSING_TOKEN: 'Missing token',
        CODE_MISSING_TOPIC: 'Missing topic',
        CODE_MISSING_PAYLOAD: 'Missing payload',
        CODE_INVALID_TOKEN_SIZE: 'Invalid token size',
        CODE_INVALID_TOPIC_SIZE: 'Invalid topic size',
        CODE_INVALID_PAYLOAD_SIZE: 'Invalid payload size',
        CODE_INVALID_TOKEN: 'Invalid token',
        CODE_SHUTDOWN: 'Shutdown',
        CODE_UNKNOWN: 'Unknown'
    }

    FORMAT = '>BBI'
    COMMAND = ERROR_RESPONSE

    def __init__(self):
        self.code = self.name = self.identifier = None

    def __str__(self):
        return '<ErrorResponse: %s>' % self.name

    def from_binary_string(self, stream):
        """Unpack the error response from a stream."""
        command, code, identifier = struct.unpack(self.FORMAT, stream)

        if command != self.COMMAND:
            raise ErrorResponseInvalidCommandError()

        if code not in self.CODES:
            raise ErrorResponseInvalidCodeError()

        self.code = code
        self.name = self.CODES[code]
        self.identifier = identifier

    def to_binary_string(self, code, identifier):
        """Pack the error response to binary string and return it."""
        return struct.pack(self.FORMAT, self.COMMAND, code, identifier)
