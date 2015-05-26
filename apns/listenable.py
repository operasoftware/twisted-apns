from collections import defaultdict


class Listenable(object):

    def __init__(self):
        self.listeners = defaultdict(list)

    def listen(self, event, callback):
        self.listeners[event].append(callback)

    def unlisten(self, event, callback):

        try:
            self.listeners[event].remove(callback)
        except ValueError:
            return False
        else:
            return True

    def dispatchEvent(self, event, *args):
        for callback in self.listeners[event]:
            callback(event, self, *args)
