import six
import abc


@six.add_metaclass(abc.ABCMeta)
class InstrumentTraits(object):

    # Return the floating point value number rounded.
    @abc.abstractmethod
    def roundQuantity(self, quantity):
        raise NotImplementedError()


class IntegerTraits(InstrumentTraits):
    def roundQuantity(self, quantity):
        return int(quantity)


