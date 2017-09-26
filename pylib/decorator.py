

__all__ = ['cached_property', 'class_property']


class cached_property(object):
    """cached property"""
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.func.__name__] = value
        return value


class class_property(object):
    """class property"""
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        value = self.func(owner)
        setattr(owner, self.func.__name__, value)
        return value
