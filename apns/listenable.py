from collections import defaultdict

from twisted.internet import defer


class Listenable(object):
    """Implements basic listener/observer model for derivative classes."""

    def __init__(self):
        self.listeners = defaultdict(list)

    def listen(self, event, callback):
        """
        Assign a callback to an event.
        :param event: an event which triggers execution of the callback.
        Particular values are defined by derivative classes.
        :param callback: a callback to be fired when event occurs.
        """
        self.listeners[event].append(callback)

    def unlisten(self, event, callback):
        """
        Remove previously assigned callback.
        :return True in case the callback was successfully removed, False
        otherwise.
        """
        try:
            self.listeners[event].remove(callback)
        except ValueError:
            return False
        else:
            return True

    @defer.inlineCallbacks
    def dispatchEvent(self, event, *args):
        """
        Fire all callbacks assigned to a particular event. To be called by
        derivative classes.
        :param *args: Additional arguments to be passed to the callback
        function.
        """
        for callback in self.listeners[event]:
            yield callback(event, self, *args)
