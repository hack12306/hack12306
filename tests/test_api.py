# encoding: utf8

import json
import pytest
import urllib
import datetime
from hack12306.api import TrainApi
from hack12306.utils import tomorrow, today
from hack12306 import exceptions

from config import COOKIES

train_api = TrainApi()


class TestTrainApi(object):
    """
    测试12306 API
    """

    # @pytest.fixture()
    # def train_api(self):
    #     return TrainApi()

    def test_query_dishonest(self):
        result = train_api.credit_query_dishonest()
        assert isinstance(result, list)

    def test_user_check_login(self):
        assert train_api.user_check_login() is False

    def test_user_info(self):
        result = train_api.user_info(cookies=COOKIES)
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_user_passengers(self):
        result = train_api.user_passengers(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_user_addressess(self):
        result = train_api.user_addresses(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_order_query(self):
        result = train_api.order_query('2018-12-02', '2018-12-31', cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_order_query_no_complete(self):
        result = train_api.order_query_no_complete(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result)

    def test_order_query_order(self):
        with pytest.raises(Exception):
            result = train_api.order_confirm_passenger_query_order('823f08e65190e9a1d2e5051d15d5fcfc', 'dc', cookies=COOKIES)
            print json.dumps(result, ensure_ascii=False)

    def test_order_result_order(self):
        with pytest.raises(Exception):
            result = train_api.order_confirm_passenger_result_order('6487212804852849745', '823f08e65190e9a1d2e5051d15d5fcfc', cookies=COOKIES)
            print json.dumps(result, ensure_ascii=False)

    def test_info_query_station_trains(self):
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        result = train_api.info_query_station_trains(today_str, 'LFV')
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_train_no(self):
        date_str = tomorrow().strftime('%Y-%m-%d')
        result = train_api.info_query_train_no('24000000G505', 'VNP', 'SHH', date_str)
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_ticket_price(self):
        date_str = tomorrow().strftime('%Y-%m-%d')
        result = train_api.info_query_ticket_price('24000000G505', '1', '2', 'WZ', date_str)
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_station_list(self):
        result = train_api.info_query_station_list()
        assert isinstance(result, list)
        print json.dumps(result[0], ensure_ascii=False)

    def test_info_query_station_by_name(self):
        result = train_api.info_query_station_by_name('北京西')
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_member_info_query_member(self):
        result = train_api.member_info_query_member(cookies=COOKIES)
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_member_info_query_member_point(self):
        result = train_api.member_info_query_member_point(cookies=COOKIES)
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_member_info_query_member_point_history(self):
        with pytest.raises(exceptions.TrainAPIException):
            start_date_str = (today() + datetime.timedelta(days=-30)).strftime('%Y%m%d')
            end_date_str = today().strftime('%Y%m%d')
            result = train_api.member_info_query_point_history('0', start_date_str, end_date_str, cookies=COOKIES)
            print json.dumps(result, ensure_ascii=False)

    def test_auth_qr_get(self):
        result = train_api.auth_qr_get()
        assert 'image' in result

    def qr_check(self):
        result = train_api.auth_qr_get()
        return train_api.auth_qr_check(result['uuid'])

    def test_auth_qr_check(self):
        result = self.qr_check()
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_auth_init(self):
        result = train_api.auth_init()
        assert isinstance(result, dict)
        print json.dumps(result, ensure_ascii=False)

    def test_info_query_left_tickets(self):
        date_str = tomorrow().strftime('%Y-%m-%d')
        result = train_api.info_query_left_tickets(date_str, 'VNP', 'SHH')
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)