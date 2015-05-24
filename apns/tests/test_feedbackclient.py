from mock import Mock, patch

from twisted.trial.unittest import TestCase

from apns.feedbackclient import (
    FeedbackClient,
    FeedbackClientFactory
)


MODULE = 'apns.feedbackclient.'


class FeedbackClientTestCase(TestCase):

    def test_connection_made(self):
        client = FeedbackClient()
        client.factory = Mock(hostname='opera.com', port=80)

        client.connectionMade()

    @patch(MODULE + 'Feedback.from_binary_string')
    def test_data_received(self, from_binary_string_mock):
        client = FeedbackClient()
        client.factory = Mock()
        data = Mock()

        client.dataReceived(data)

        from_binary_string_mock.assert_called_once_with(data)
        client.factory.feedbacksReceived(from_binary_string_mock.return_value)


class FeedbackClientFactoryTestCase(TestCase):

    @patch(MODULE + 'ssl.PrivateCertificate.loadPEM', Mock())
    @patch(MODULE + 'FeedbackClientFactory.ENDPOINTS', {'pub': ('foo', 'bar')})
    def setUp(self):
        self.onFeedbacksReceived = Mock()
        self.factory = FeedbackClientFactory('pub', __file__,
                                             self.onFeedbacksReceived)

    @patch(MODULE + 'ReconnectingClientFactory.clientConnectionFailed')
    def test_client_connection_failed(self, client_connection_failed_mock):
        connector = Mock()
        reason = Mock()

        self.factory.clientConnectionFailed(connector, reason)

        client_connection_failed_mock.assert_called_once_with(self.factory,
                                                              connector,
                                                              reason)

    @patch(MODULE + 'ReconnectingClientFactory.clientConnectionLost')
    def test_client_connection_lost(self, client_connection_lost_mock):
        connector = Mock()
        reason = Mock()

        self.factory.clientConnectionLost(connector, reason)

        client_connection_lost_mock.assert_called_once_with(self.factory,
                                                            connector,
                                                            reason)

    def test_feedbacks_received(self):
        feedbacks = Mock()

        self.factory.feedbacksReceived(feedbacks)

        self.onFeedbacksReceived.assert_called_once_with(feedbacks)

    def test_feedbacks_received_no_callback(self):
        self.factory.onFeedbacksReceived = None

        self.factory.feedbacksReceived(Mock())
