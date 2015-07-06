# Twisted client for APNs
[![Build status](https://travis-ci.org/operasoftware/twisted-apns.svg)](https://travis-ci.org/operasoftware/twisted-apns)
[![Version](https://img.shields.io/pypi/v/twisted-apns.svg)](https://pypi.python.org/pypi/twisted-apns)
[![Code Climate](https://codeclimate.com/github/operasoftware/twisted-apns/badges/gpa.svg)](https://codeclimate.com/github/operasoftware/twisted-apns)

Based on [official iOS documentation](https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/CommunicatingWIthAPS.html).
## Usage

```python
import logging

from apns.gatewayclient import GatewayClientFactory
from apns.notification import Notification
from twisted.internet import reactor


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Make sure /apn-dev.pem exists or pass valid path.
factory = GatewayClientFactory('dev', '/apn-dev.pem')
reactor.connectSSL(factory.hostname,
                   factory.port,
                   factory,
                   factory.certificate.options())

def send():
    token = '00'  # Set to something valid.
    payload = {'aps': {'alert': "What's up?",
                       'sound': 'default',
                       'badge': 3}}
    notification = Notification(token=token,
                                expire=Notification.EXPIRE_IMMEDIATELY,
                                payload=payload)
    factory.send(notification)

reactor.callLater(1, send)
reactor.run()
```

If `token` is valid console outputs:
```
Gateway connection made: gateway.push.apple.com:2195
Gateway send notification
```


If not (like `00`) error is returned:
```
Gateway connection made: gateway.sandbox.push.apple.com:2195
Gateway send notification
Gateway error received: <ErrorResponse: Invalid token>
Gateway connection lost: Connection was closed cleanly.
Gateway connection made: gateway.sandbox.push.apple.com:2195
```

