from mock import patch
from twisted.trial.unittest import TestCase

from apns.errorresponse import (
    ErrorResponse,
    ErrorResponseInvalidCodeError,
    ErrorResponseInvalidCommandError
)


MODULE = 'apns.errorresponse.'


class ErrorResponseTestCase(TestCase):
    CLASS = MODULE + 'ErrorResponse.'

    def test_str(self):
        resp = ErrorResponse()
        resp.name = 'name'

        self.assertEqual(str(resp), '<ErrorResponse: name>')

    @patch(CLASS + 'CODES', {0: 'invalid token'})
    @patch(MODULE + 'struct.unpack')
    def test_properties_set(self, unpack_mock):
        unpack_mock.return_value = ErrorResponse.COMMAND, 0, 'identifier'
        resp = ErrorResponse()

        resp.from_binary_string('stream')

        self.assertEqual(resp.code, 0)
        self.assertEqual(resp.name, 'invalid token')
        self.assertEqual(resp.identifier, 'identifier')

    @patch(MODULE + 'struct.unpack')
    def test_from_binary_string_invalid_command(self, unpack_mock):
        unpack_mock.return_value = ErrorResponse.COMMAND + 1, None, None
        resp = ErrorResponse()

        with self.assertRaises(ErrorResponseInvalidCommandError):
            resp.from_binary_string('stream')

    @patch(CLASS + 'CODES', {0: 'invalid token'})
    @patch(MODULE + 'struct.unpack')
    def test_from_binary_string_invalid_code(self, unpack_mock):
        unpack_mock.return_value = ErrorResponse.COMMAND, 1, None
        resp = ErrorResponse()

        with self.assertRaises(ErrorResponseInvalidCodeError):
            resp.from_binary_string('stream')

    @patch(CLASS + 'CODES', {0: 'invalid token'})
    def test_from_binary_string_valid_input(self):
        resp = ErrorResponse()
        resp.from_binary_string(resp.to_binary_string(0, 123))

        self.assertEqual(resp.code, 0)
        self.assertEqual(resp.name, 'invalid token')
        self.assertEqual(resp.identifier, 123)
