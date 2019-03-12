# encoding: utf8
"""
utils.py
@author Meng.yangyang
@description Util functions
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import six
import uuid
import json
import urllib
import decimal
import datetime


def cookie_str_to_dict(cookie_str):
    cookies = []
    for cookie in [cookie.strip() for cookie in cookie_str.split(';')]:
        cookies.append((cookie.split('=')[0], ''.join(cookie.split('=')[1:])))
    return dict(cookies)


def get_cookie_from_str(cookie_str):
    cookie_dict = cookie_str_to_dict(cookie_str)
    return {
        'BIGipServerotn': cookie_dict.get('BIGipServerotn', ''),
        'JSESSIONID': cookie_dict.get('JSESSIONID', ''),
        'tk': cookie_dict.get('tk', ''),
        'route': cookie_dict.get('route', ''),
    }


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def today():
    return datetime.date.today()


def urlencode(params):
    assert isinstance(params, (list, dict))

    if isinstance(params, list):
        param_list = []
        for param in params:
            param_list.append(urllib.urlencode({param[0]: param[1]}))
        return '&'.join(param_list)
    elif isinstance(params, dict):
        return urllib.urlencode(params)
    else:
        assert False, 'Unsupported type params'


def time_cst_format(time):
    """
    格式化为 CST 格式时间
    """
    CST_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
    assert isinstance(time, datetime.datetime), 'Invalid time param. %s' % time
    return time.strftime(CST_FORMAT)


class JSONEncoder(json.JSONEncoder):

    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, generators and other basic python objects.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            representation = obj.isoformat()
            return representation
        elif isinstance(obj, datetime.timedelta):
            return six.text_type(obj.total_seconds())
        elif isinstance(obj, decimal.Decimal):
            # Serializers will coerce decimals to strings by default.
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return six.text_type(obj)
        elif isinstance(obj, bytes):
            # Best-effort for binary blobs. See #4187.
            return obj.decode('utf-8')
        elif hasattr(obj, 'tolist'):
            # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except Exception:
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super(JSONEncoder, self).default(obj)


def gen_passenger_ticket_tuple(seat_type, passenger_flag, passenger_type,
                               name, id_type, id_no, mobile, **kwargs):
    l = [seat_type, passenger_flag, passenger_type, name, id_type, id_no, mobile, 'N']
    return tuple([unicode(i).encode('utf8') for i in l])


def gen_old_passenge_tuple(name, id_type, id_no, passenger_type, **kwargs):
    l = [name, id_type, id_no,  str(passenger_type)+'_']
    return tuple([unicode(i).encode('utf8') for i in l])
