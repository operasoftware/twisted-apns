from mock import Mock
from twisted.trial.unittest import TestCase

from apns.listenable import Listenable


class ListenableTestCase(TestCase):

    def setUp(self):
        self.listenable = Listenable()

    def test_listen(self):
        event = 'foo'
        callback = object()

        self.listenable.listen(event, callback)

        self.assertEqual(self.listenable.listeners[event], [callback])

    def test_unlisten_unknown_event(self):
        self.assertFalse(self.listenable.unlisten('foo', object()))

    def test_unlisten_unknown_callback(self):
        event = 'foo'
        self.listenable.listen(event, object())

        self.assertFalse(self.listenable.unlisten(event, object()))

    def test_unlisten(self):
        event = 'foo'
        callback = object()
        self.listenable.listen(event, callback)

        self.assertTrue(self.listenable.unlisten(event, callback))

    def test_dispatch_event_no_callbacks(self):
        self.listenable.dispatchEvent('foo')

    def test_dispatch_event(self):
        event = 'foo'
        callback_1 = Mock()
        callback_2 = Mock()
        param_1 = Mock()
        param_2 = Mock()
        self.listenable.listen(event, callback_1)
        self.listenable.listen(event, callback_2)

        self.listenable.dispatchEvent(event, param_1, param_2)

        callback_1.assert_called_once_with(event, self.listenable, param_1,
                                           param_2)
        callback_2.assert_called_once_with(event, self.listenable, param_1,
                                           param_2)
