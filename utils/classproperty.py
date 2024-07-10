"""Module that holds the `classproperty` decorator"""


class classproperty(property):  # pylint: disable=invalid-name
    """Decorator to create a class property.\
        creates a read only class property so that it doesn't\
            have to be reinitialized every time a class is instantiated

    Args:
        - `property` (property): property to wrap.\n
    Returns:
        `property`: Wrapped property."""

    def __get__(self, owner_self: object, owner_cls: object):
        return self.fget(owner_cls)
