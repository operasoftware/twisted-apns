import logging

from twisted.internet import defer, ssl
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from apns.feedback import Feedback
from apns.listenable import Listenable


logger = logging.getLogger(__name__)


class FeedbackClient(Protocol):
    """
    Implements client-side of APN feedback service protocol. Should be spawned
    by FeedbackClientFactory and generally should not be used standalone.
    """
    def connectionMade(self):
        logger.debug('Feedback connection made: %s:%d', self.factory.hostname,
                     self.factory.port)

    @defer.inlineCallbacks
    def dataReceived(self, data):
        feedbacks = Feedback.from_binary_string(data)
        yield self.factory.feedbacksReceived(feedbacks)


class FeedbackClientFactory(ReconnectingClientFactory, Listenable):
    """
    Allows connecting to the APN feedback service and receiving feedback
    information. To process received feedbacks in your code, add a callback to
    EVENT_FEEDBACKS_RECEIVED.
    """
    protocol = FeedbackClient
    maxDelay = 600
    ENDPOINTS = {
        'pub': ('feedback.push.apple.com', 2196),
        'dev': ('feedback.sandbox.push.apple.com', 2196)
    }
    EVENT_FEEDBACKS_RECEIVED = 'feedbacks received'

    def __init__(self, endpoint, pem):
        """
        Init an instance of FeedbackClientFactory.
        :param endpoint: Either 'pub' for production or 'dev' for development.
        :param pem: Path to a provider private certificate file.
        """
        Listenable.__init__(self)
        self.hostname, self.port = self.ENDPOINTS[endpoint]
        self.client = None

        with open(pem) as f:
            self.certificate = ssl.PrivateCertificate.loadPEM(f.read())

    @defer.inlineCallbacks
    def feedbacksReceived(self, feedbacks):
        logger.debug('Feedbacks received: %s', feedbacks)
        yield self.dispatchEvent(self.EVENT_FEEDBACKS_RECEIVED, feedbacks)

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
