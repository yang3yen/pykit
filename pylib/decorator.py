

import functools


__all__ = ['cached_property']


class cached_property(object):
    """cached property"""
    def __int__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.func.__name__] = value
        return value
