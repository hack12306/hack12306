# encoding: utf8

import urllib
import datetime


def cookie_str_to_dict(cookie_str):
    cookies = []
    for cookie in [cookie.strip() for cookie in cookie_str.split(';')]:
        cookies.append(cookie.split('='))
    return dict(cookies)


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
