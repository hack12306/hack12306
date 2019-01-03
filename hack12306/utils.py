# encoding: utf8

import urllib
import datetime


def cookie_str_to_dict(cookie_str):
    cookies = []
    for cookie in [cookie.strip() for cookie in cookie_str.split(';')]:
        cookies.append(cookie.split('='))
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
    assert isinstance(params, list)

    query_string_list = []
    for param in params:
        query_string_list.append(urllib.urlencode({param[0]: param[1]}))

    return '&'.join(query_string_list)


def time_cst_format(time):
    """
    格式化为 CST 格式时间
    """
    CST_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
    assert isinstance(time, datetime.datetime), 'Invalid time param. %s' % time
    return time.strftime(CST_FORMAT)
