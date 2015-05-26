import logging

from twisted.internet import ssl
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from apns.feedback import Feedback
from apns.listenable import Listenable


logger = logging.getLogger(__name__)


class FeedbackClient(Protocol):
    def connectionMade(self):
        logger.debug('Feedback connection made: %s:%d', self.factory.hostname,
                     self.factory.port)

    def dataReceived(self, data):
        feedbacks = Feedback.from_binary_string(data)
        self.factory.feedbacksReceived(feedbacks)


class FeedbackClientFactory(ReconnectingClientFactory, Listenable):
    protocol = FeedbackClient
    maxDelay = 600
    ENDPOINTS = {
        'pub': ('feedback.push.apple.com', 2196),
        'dev': ('feedback.sandbox.push.apple.com', 2196)
    }
    EVENT_FEEDBACKS_RECEIVED = 'feedbacks received'

    def __init__(self, endpoint, pem):
        Listenable.__init__(self)
        self.hostname, self.port = self.ENDPOINTS[endpoint]
        self.client = None

        with open(pem) as f:
            self.certificate = ssl.PrivateCertificate.loadPEM(f.read())

    def feedbacksReceived(self, feedbacks):
        logger.debug('Feedbacks received: %s', feedbacks)
        self.dispatchEvent(self.EVENT_FEEDBACKS_RECEIVED, feedbacks)

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
