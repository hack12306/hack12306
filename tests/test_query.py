# encoding: utf8

import json
import pytest
import urllib
import datetime

from hack12306.query import TrainInfoQueryAPI
from hack12306.utils import tomorrow, today
from hack12306 import exceptions

from config import COOKIES

train_info_query_api = TrainInfoQueryAPI()


class TestTrainInfoQueryAPI(object):
    """
    测试12306信息查询API
    """

    def test_info_query_station_trains(self):
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        result = train_info_query_api.info_query_station_trains(today_str, 'LFV')
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_train_no(self):
        date_str = tomorrow().strftime('%Y-%m-%d')
        result = train_info_query_api.info_query_train_no('24000000G505', 'VNP', 'SHH', date_str)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_ticket_price(self):
        with pytest.raises(Exception):
            date_str = tomorrow().strftime('%Y-%m-%d')
            result = train_info_query_api.info_query_ticket_price('24000000G505', '1', '2', 'WZ', date_str)
            assert isinstance(result, dict)
            print json.dumps(result, ensure_ascii=False)

    def test_info_query_station_list(self):
        result = train_info_query_api.info_query_station_list()
        assert isinstance(result, list)
        print json.dumps(result[0], ensure_ascii=False)

    def test_info_query_station_by_name(self):
        result = train_info_query_api.info_query_station_by_name('北京西')
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)