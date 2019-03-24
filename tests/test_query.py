# encoding: utf8

import json
import pytest
import urllib
import datetime

from hack12306 import exceptions
from hack12306.query import TrainInfoQueryAPI
from hack12306.utils import tomorrow, today

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
        result = train_info_query_api.info_query_station_by_name(u'北京西')
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_left_tickets(self):
        date_str = tomorrow().strftime('%Y-%m-%d')
        result = train_info_query_api.info_query_left_tickets(date_str, 'MCN', 'BJP')
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_train_search(self):
        result = train_info_query_api.info_query_train_search('K571')
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_dishonest(self):
        result = train_info_query_api.info_query_dishonest()
        assert isinstance(result, list)

    def test_info_query_dishonest_getone(self):
        result = train_info_query_api.info_query_dishonest_getone('孟', '131122')
        assert isinstance(result, list)

    def test_info_query_trains(self):
        result = train_info_query_api.info_query_trains()
        assert isinstance(result, list)
        print json.dumps(result[0], ensure_ascii=False)
