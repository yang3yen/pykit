# -*- coding: utf-8 -*-


import six
from itertools import chain


__all__ = ['is_iterable', 'makelist', 'difference', 'intersection']


def is_iterable(obj):
    """判断对象是否是可迭代的,是返回True,否则返回False."""
    is_iter = True
    try:
        iter(obj)
    except TypeError:
        is_iter = False
    return is_iter


def makelist(data):
    """make list"""
    if isinstance(data, six.string_types):
        return [data]
    elif is_iterable(data):
        return list(data)
    else:
        return [data]


def difference(iterable, *other_iterable):
    res, des = list(iterable), set(chain(*other_iterable))
    return [v for v in res if v not in des]


def intersection(iterable, *other_iterable):
    res, des = list(iterable), set(chain(*other_iterable))
    return [v for v in res if v in des]
