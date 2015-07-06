import logging

from twisted.internet import ssl
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from apns.errorresponse import ErrorResponse
from apns.listenable import Listenable


logger = logging.getLogger(__name__)


class GatewayClientError(Exception):
    """To be thrown upon failures on communication with APN gateway."""
    pass


class GatewayClientNotSetError(GatewayClientError):
    """
    Thrown when attempted to send a notification while connection is not
    established.
    """
    pass


class GatewayClient(Protocol):
    """
    Implements client-side of APN gateway protocol. Should be spawned by
    GatewayClientFactory and generally should not be used standalone.
    """
    def connectionMade(self):
        logger.debug('Gateway connection made: %s:%d', self.factory.hostname,
                     self.factory.port)
        self.factory.connectionMade(self)

    def send(self, notification):
        stream = notification.to_binary_string()
        self.transport.write(stream)

    def dataReceived(self, data):
        error = ErrorResponse()
        error.from_binary_string(data)
        self.factory.errorReceived(error)


class GatewayClientFactory(ReconnectingClientFactory, Listenable):
    """Allows connecting to the APN gateway and sending notifications."""
    protocol = GatewayClient
    maxDelay = 10
    ENDPOINTS = {
        'pub': ('gateway.push.apple.com', 2195),
        'dev': ('gateway.sandbox.push.apple.com', 2195)
    }
    EVENT_ERROR_RECEIVED = 'error received'
    EVENT_CONNECTION_MADE = 'connection made'
    EVENT_CONNECTION_LOST = 'connection lost'

    def __init__(self, endpoint, pem):
        """
        Init an instance of GatewayClientFactory.
        :param endpoint: Either 'pub' for production or 'dev' for development.
        :param pem: Path to a provider private certificate file.
        """
        Listenable.__init__(self)
        self.hostname, self.port = self.ENDPOINTS[endpoint]
        self.client = None

        with open(pem) as f:
            self.certificate = ssl.PrivateCertificate.loadPEM(f.read())

    def connectionMade(self, client):
        self.client = client
        self.dispatchEvent(self.EVENT_CONNECTION_MADE)

    def _onConnectionLost(self):
        self.client = None
        self.dispatchEvent(self.EVENT_CONNECTION_LOST)

    def errorReceived(self, error):
        logger.debug('Gateway error received: %s', error)
        self.dispatchEvent(self.EVENT_ERROR_RECEIVED, error)

    def clientConnectionFailed(self, connector, reason):
        logger.debug('Gateway connection failed: %s',
                     reason.getErrorMessage())
        self._onConnectionLost()
        return ReconnectingClientFactory.clientConnectionFailed(self,
                                                                connector,
                                                                reason)

    def clientConnectionLost(self, connector, reason):
        logger.debug('Gateway connection lost: %s',
                     reason.getErrorMessage())
        self._onConnectionLost()
        return ReconnectingClientFactory.clientConnectionLost(self,
                                                              connector,
                                                              reason)

    @property
    def connected(self):
        """Return True if connection with APN is established."""
        return self.client is not None

    def send(self, notification):
        """Send prepared notification to the APN."""
        logger.debug('Gateway send notification')

        if self.client is None:
            raise GatewayClientNotSetError()

        self.client.send(notification)
