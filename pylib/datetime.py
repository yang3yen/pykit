#! -*- coding: utf-8 -*-


from __future__ import absolute_import

import re
import six
import pytz

from numbers import Integral, Real
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, time, timedelta
from .collections import makelist, is_iterable


__all__ = ['parse_datetime', 'parse_timedelta', 'is_naive', 'to_naive',
           'convert_tz', 'T', 'TZ', 'TD']


def parse_datetime(dt, force_datetime=True):
    """
    Try convert single or seq of int/str/datetime/date values to datetime.
    :param dt: single value or seq of:
                    int/str: YYYYMMDD[HH[MM[SS]]] , delimiters are also allowed, 
                        e.g.: YYYY-MM-DD HH:MM:SS.
                        Julian Days, e.g., YYYYJJJ[...] is also OK.
                    datetime/date
    :param force_datetime: 
                    if True: return datetime even if input is date.
                    if False: return date if input is date.
    :return datetime
    """
    jfmtstr_all = '%Y%j%H%M%S'
    gfmtstr_all = '%Y%m%d%H%M%S'
    
    is_seq = is_iterable(dt) and not isinstance(dt, six.string_types)
    
    dts = []
    for dt in makelist(dt):
        if not isinstance(dt, (Integral, six.string_types, datetime, date)):
            dts.append(None)
            continue
            
        # datetime
        if isinstance(dt, datetime):
            dts.append(dt)
            continue
        # date
        if isinstance(dt, date):
            if force_datetime:
                dts.append(datetime.fromordinal(dt.toordinal()))
            else:
                dts.append(dt)
            continue

        # int, np.integer
        if isinstance(dt, Integral):
            dt = str(dt)
            
        # str
        if len(dt) == 10:
            if re.match(r'^\d{10}$', dt):
                dt = dt + '00'
            elif re.match(r'^\d{4}.\d{2}.\d{2}$', dt):
                dt = dt + ' 00:00:00'
                
        try:
            res = parse(dt)
        except (ValueError, Exception):
            try:
                numonly_str = re.sub(r'\D*', '', dt)
                nl = len(numonly_str)
                if nl >= 7:   
                    # YYYYJJJ[...]
                    if nl % 2 == 1:
                        fmtstr = jfmtstr_all[:4+nl-7]
                    else:             
                        # YYYYMMDD[...]
                        fmtstr = gfmtstr_all[:6+nl-8]
                    res = datetime.strptime(numonly_str, fmtstr)
                else:
                    res = parse(numonly_str)
            except (ValueError, Exception):
                res = None
        dts.append(res)
        
    return dts if is_seq else dts[0]


def parse_timedelta(td):
    """
    Try parse single value or seq of string/integer/float/timedelta to timedelta.
    eg: parse ['15', '30m', '-2h', '1d', '1M', '-2Y']
     Y: years
     M: months
     W: weeks
     d: days
     h: hours
     m: minutes
     s: seconds (default)
     ms: microseconds
    :param td: type is (string, integer, float, timedelta, relativedelta)
    :return: relativedelta
    """
    _td_fmt = {
        'Y': 'years',
        'M': 'months',
        'W': 'weeks',
        'd': 'days',
        'h': 'hours',
        'm': 'minutes',
        's': 'seconds',  # default
        'ms': 'microseconds'
    }

    is_seq = is_iterable(td) and not isinstance(td, six.string_types)

    tds = []
    for td in makelist(td):
        if not isinstance(td, (Real, six.string_types, timedelta, relativedelta)):
            tds.append(None) 
            continue
        if isinstance(td, timedelta):
            tds.append(relativedelta(seconds=td.total_seconds()))
            continue
        if isinstance(td, relativedelta):
            tds.append(td)
            continue

        if isinstance(td, Real):
            td = str(td)
        td = td.strip()

        match = re.match(r'^(?P<value>[-+]?[0-9]*\.?[0-9]*)(?P<symbol>(?:[YMWdhms]?|ms)$)', td)
        if not match:
            td = None
        else:
            value = match.group('value')
            value = float(value) if '.' in value else int(value)
            symbol = match.group('symbol')
            td = relativedelta(**{_td_fmt.get(symbol, 'seconds'): value})
        tds.append(td)
    return tds if is_seq else tds[0]


def is_naive(dt):
    """
    Whether an object of type time or datetime is naive, is naive return True, otherwise return False.
    :param dt: an object of type time or datetime
    :return: bool
    """
    if not isinstance(dt, (time, datetime)):
        raise TypeError('{} is not an object of type time or datetime'.format(dt))
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def to_naive(dt):
    """
    Convert an object of type time or datetime to naive.
    :param dt: an object of type time or datetime
    :return: time or datetime
    """
    if not isinstance(dt, (time, datetime)):
        raise TypeError('{} is not an object of type time or datetime'.format(dt))
    return dt.replace(tzinfo=None)


def convert_tz(dt, tz='UTC', naive=False):
    """
    Convert to a datetime in new timezone tz.
    :param dt: single value or seq of:
                int/str: YYYYMMDD[HH[MM[SS]]] , delimiters are also allowed,
                    e.g.: YYYY-MM-DD HH:MM:SS.
                    Julian Days, e.g., YYYYJJJ[...] is also OK.
                datetime/date
    :param tz: timezone, default is 'UTC'
    :param naive: whether return datetime is naive, default is False.
    :return: single or list of datetime
    """
    is_seq = is_iterable(dt) and not isinstance(dt, basestring)
    timezone = pytz.timezone(zone=tz)

    dts = []
    for dt in makelist(parse_datetime(dt)):
        if isinstance(dt, datetime):
            dt = timezone.localize(dt) if is_naive(dt) else dt.astimezone(tz=timezone)
            if naive:
                dt = to_naive(dt)
            dts.append(dt)
        else:
            dts.append(dt)
    return dts if is_seq else dts[0]

    
T = parse_datetime
TZ = convert_tz
TD = parse_timedelta
