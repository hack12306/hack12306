# encoding: utf8
"""
base.py
@author Meng.yangyang
@description Wrapper network request
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import re
import copy
import time
import json
import urllib
import logging
import datetime
import requests
import collections

from . import settings
from . import constants
from . import exceptions
from .utils import urlencode, tomorrow, time_cst_format

_logger = logging.getLogger('hack12306')

__all__ = ('TrainBaseAPI',)


def _debug_resp(url, resp):
    import os
    import uuid
    import datetime

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    filepath = '/tmp/hack12306/%s/%s-%s' % (today_str, url, uuid.uuid1().hex)
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'w') as f:
        f.write(resp.content)


class TrainBaseAPI(object):
    """
    12306 Train API.
    """

    def submit(self, url, params=None, method='POST', format='form', parse_resp=True, **kwargs):
        _logger.debug('train request. url:%s method:%s params:%s' % (url, method, json.dumps(params)))

        headers = kwargs.get('headers', {})
        headers.update(**self.headers)
        kwargs['headers'] = headers

        if method == 'GET':
            if isinstance(params, list):
                params = urlencode(params)
            resp = requests.get(url, params, **kwargs)
        elif method == 'POST':
            if format == 'json':
                resp = requests.post(url, json=params, **kwargs)
            else:
                resp = requests.post(url, data=params, **kwargs)
        else:
            assert False, 'Unknown http method'

        if not parse_resp:
            return resp

        if resp.status_code != 200:
            if settings.DEBUG:
                _debug_resp(url, resp)
            raise exceptions.TrainRequestException(str(resp))

        try:
            content_json = json.loads(resp.content)
        except ValueError as e:
            if settings.DEBUG:
                _debug_resp(url, resp)

            _logger.warning(e)
            raise exceptions.TrainRequestException('response is not valid json type')

        if content_json['status'] is not True:
            _logger.warning('%s resp. %s' % (url, resp.content))
            raise exceptions.TrainAPIException(resp.content)

        return content_json

    @property
    def headers(self):
        return {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'),
        }
