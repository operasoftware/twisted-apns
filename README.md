# Twisted client for APNs
[![Build status](https://travis-ci.org/operasoftware/twisted-apns.svg)](https://travis-ci.org/operasoftware/twisted-apns)
[![Version](https://img.shields.io/pypi/v/twisted-apns.svg)](https://pypi.python.org/pypi/twisted-apns)
[![Code Climate](https://codeclimate.com/github/operasoftware/twisted-apns/badges/gpa.svg)](https://codeclimate.com/github/operasoftware/twisted-apns)

## Overview
*Twisted-APNs* is an implementation of provider-side client for Apple Push Notification Service, based on [official iOS documentation](https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/CommunicatingWIthAPS.html). It uses [Twisted networking engine](https://twistedmatrix.com).

## Features
* Sending notifications through gateway service
* Querying feedback service for failed remote notifications

## Requirements
* Python>=2.7
* Twisted (version 15.0.0 known to work)
* pyOpenSSL

## Download
* [GitHub](https://github.com/operasoftware/twisted-apns)

## Installation
You can install it easily from PyPi by single command:
```
pip install twisted-apns
```
or clone source code and run:
```
python setup.py install
```

## Usage examples

### Sending a notification

First, do the necessary imports and set up logging for debug purposes:
```python
import logging

from apns.gatewayclient import GatewayClientFactory
from apns.notification import Notification
from twisted.internet import reactor


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
```

Then create an instance of gateway client factory, specifying intended endpoint (`pub` for production or `dev` for development purposes), and setting a path to your provider certificate:
```python
# Make sure /apn-dev.pem exists or pass valid path.
factory = GatewayClientFactory('dev', '/apn-dev.pem')
reactor.connectSSL(factory.hostname,
                   factory.port,
                   factory,
                   factory.certificate.options())
```
The code below sends a sample notification with JSON-encoded payload to device identified with supplied `token` (in hex):
```python
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
Gateway error received: <ErrorResponse: Invalid token size>
Gateway connection lost: Connection was closed cleanly.
Gateway connection made: gateway.sandbox.push.apple.com:2195
```

### Querying list of invalidated tokens

The following code connects to the feedback service and prints tokens which should not be used anymore:
```python
import logging

from apns.feedbackclient import FeedbackClientFactory
from apns.feedback import Feedback
from twisted.internet import reactor

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Make sure /apn-dev.pem exists or pass valid path.
factory = FeedbackClientFactory('dev', '/apn-dev.pem')
reactor.connectSSL(factory.hostname,
                   factory.port,
                   factory,
                   factory.certificate.options())

def onFeedbacks(feedbacks):
    for f in feedbacks:
        print "It would be better to stop sending notifications to", f.token

factory.listen(FeedbackClientFactory.EVENT_FEEDBACKS_RECEIVED, onFeedbacks)

reactor.run()
```

## Contributing
You are highly encouraged to participate in the development, simply use GitHub's fork/pull request system.
