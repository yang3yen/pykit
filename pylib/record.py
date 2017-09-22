#! -*- coding: utf-8 -*-

from __future__ import absolute_import
from collections import namedtuple


__all__ = ['NamedRecord']


class NamedRecord(object):
    """
    namedtuple的封装, 增加字段类型的转换
    >>> Point = NamedRecord('Point', 'x y', {'x': float})
    >>> Point(x='1', y=1.0)
    Point(x=1.0, y=1.0)
    """
    def __init__(self, typename, field_names,
                 field_trans_func_d=None):
        self.record = namedtuple(typename, field_names)
        if field_trans_func_d is not None and \
                not isinstance(field_trans_func_d, dict):
            raise TypeError('{} is not a dict'.format(field_trans_func_d))
        self.field_trans_func_d = field_trans_func_d

    def __call__(self, *args, **kwargs):
        as_dict = kwargs.pop('as_dict', False)

        rd = self.record(*args, **kwargs)
        if self.field_trans_func_d is not None:
            _field_d = rd.__dict__.copy()
            for field, trans_func in self.field_trans_func_d.items():
                if callable(trans_func):
                    _field_d[field] = trans_func(_field_d[field])
            rd = self.record(**_field_d)
        return rd.__dict__.copy() if as_dict else rd

    def __repr__(self):
        return repr(self.record)
