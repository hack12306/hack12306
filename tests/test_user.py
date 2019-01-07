# encoding: utf8

import json
import pytest
import urllib
import datetime

from hack12306.user import TrainUserAPI
from config import COOKIES

train_user_api = TrainUserAPI()


class TestTrainUserAPI(object):
    """
    测试12306用户API
    """
    def test_user_info(self):
        result = train_user_api.user_info(cookies=COOKIES)
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_user_passengers(self):
        result = train_user_api.user_passengers(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_user_addressess(self):
        result = train_user_api.user_addresses(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)
