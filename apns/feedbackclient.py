import logging

from twisted.internet import ssl
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from apns.feedback import Feedback


logger = logging.getLogger(__name__)


class FeedbackClient(Protocol):
    def connectionMade(self):
        logger.debug('Feedback connection made: %s:%d', self.factory.hostname,
                     self.factory.port)

    def dataReceived(self, data):
        feedbacks = Feedback.from_binary_string(data)
        self.factory.feedbacksReceived(feedbacks)


class FeedbackClientFactory(ReconnectingClientFactory):
    protocol = FeedbackClient
    maxDelay = 600
    ENDPOINTS = {
        'pub': ('feedback.push.apple.com', 2196),
        'dev': ('feedback.sandbox.push.apple.com', 2196)
    }

    def __init__(self, endpoint, pem, onFeedbacksReceived=None):
        self.hostname, self.port = self.ENDPOINTS[endpoint]
        self.client = None
        self.onFeedbacksReceived = onFeedbacksReceived

        with open(pem) as f:
            self.certificate = ssl.PrivateCertificate.loadPEM(f.read())

    def feedbacksReceived(self, feedbacks):
        logger.debug('Feedbacks received: %s', feedbacks)

        if self.onFeedbacksReceived:
            self.onFeedbacksReceived(feedbacks)

    def clientConnectionFailed(self, connector, reason):
        logger.debug('Feedback connection failed: %s',
                     reason.getErrorMessage())
        return ReconnectingClientFactory.clientConnectionFailed(self,
                                                                connector,
                                                                reason)

    def clientConnectionLost(self, connector, reason):
        logger.debug('Feedback connection lost: %s',
                     reason.getErrorMessage())
        return ReconnectingClientFactory.clientConnectionLost(self,
                                                              connector,
                                                              reason)
