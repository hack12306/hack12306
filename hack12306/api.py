# encoding: utf8

import json
import logging
import requests

from . import exceptions

_logger = logging.getLogger('hack12306')


class TrainApi(object):
    """
    12306 Train API.
    """

    def submit(self, url, params=None, method='POST', format='json', **kawrgs):
        _logger.debug('train request. url:%s method:%s params:%s' % (url, method, json.dumps(params)))

        if method == 'GET':
            resp = requests.get(url, params)
        elif method == 'POST':
            handler = requests.post
            if format == 'json':
                resp = handler(url, json=params)
            else:
                resp = handler(url, data=params)
        else:
            assert False, 'Unknown http method'

        if resp.status_code != 200:
            raise exceptions.TrainAPIException()

        content_json = json.loads(resp.content)
        if content_json['status'] is not True:
            raise exceptions.TrainAPIException(content_json['errMsg'])

        return content_json

    def query_dishonest(self, **kwargs):
        """
        失信已执行名单
        """
        url = 'https://dynamic.12306.cn/otn/queryDishonest/query'
        return self.submit(url, method='GET')

