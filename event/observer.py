import abc

import six

from config import dispatchprio


class Event(object):
    def __init__(self):
        self.__handlers = []
        self.__deferred = []
        self.__emitting = 0

    def __subscribe_impl(self, handler):
        assert not self.__emitting
        if handler not in self.__handlers:
            self.__handlers.append(handler)

    def __unsubscribe_impl(self, handler):
        assert not self.__emitting
        self.__handlers.remove(handler)

    def __apply_changes(self):
        assert not self.__emitting
        for action, param in self.__deferred:
            action(param)
        self.__deferred = []

    def subscribe(self, handler):
        if self.__emitting:
            self.__deferred.append((self.__subscribe_impl, handler))
        elif handler not in self.__handlers:
            self.__subscribe_impl(handler)

    def unsubscribe(self, handler):
        if self.__emitting:
            self.__deferred.append((self.__unsubscribe_impl, handler))
        else:
            self.__unsubscribe_impl(handler)

    def emit(self, *args, **kwargs):
        try:
            self.__emitting += 1
            for handler in self.__handlers:
                handler(*args, **kwargs)
        finally:
            self.__emitting -= 1
            if not self.__emitting:
                self.__apply_changes()


@six.add_metaclass(abc.ABCMeta)
class Subject(object):

    def __init__(self):
        self.__dispatch_priority = dispatchprio.LAST

    # This may raise.
    @abc.abstractmethod
    def start(self):
        pass

    # This should not raise.
    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError()

    # This should not raise.
    @abc.abstractmethod
    def join(self):
        raise NotImplementedError()

    # Return True if there are not more events to dispatch.
    @abc.abstractmethod
    def eof(self):
        raise NotImplementedError()

    # Dispatch events. If True is returned, it means that at least one event was dispatched.
    @abc.abstractmethod
    def dispatch(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def peek_datetime(self):
        # Return the datetime for the next event.
        # This is needed to properly synchronize non-realtime subjects.
        # Return None since this is a realtime subject.
        raise NotImplementedError()

    @property
    def dispatch_priority(self):
        return self.__dispatch_priority

    @dispatch_priority.setter
    def dispatch_priority(self, value):
        self.__dispatch_priority = value

    def on_dispatch_priority_registered(self, dispatcher):
        # Called when the subject is registered with a dispatcher.
        pass
