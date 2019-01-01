# encoding: utf8

import json
import pytest
import datetime
from hack12306.api import TrainApi
from hack12306.utils import tomorrow, today
from hack12306 import exceptions

train_api = TrainApi()

COOKIES = {
    "BIGipServerpool_tlcx": "48235018.31270.0000",
    "RAIL_DEVICEID": "Dv9nY4_XzkbPhbA2wlkpuJ39PRw9LB-edng2VfjfYG3lcu6wKLR5PSF6LzzPc3WvbNuXVX_BN3R0ABFl6Ms_nccEBGM51kc6kg-XKryfTxtTv8_8pGXJxUfUXS8TcFEhQB_uvqNsfemB10Wjh4SdlCN-JAbEkb7E",
    "route": "7476ffad615b7b71cbf5b6e46add2a8a",
    "JSESSIONID": "CDC4105F76D9D777956065A99D5F6D3D",
    "tk": "r3phpjBJ2Sm_1czN9sPQdRKYFu1c41D4ntDiKArwh2h0",
    "RAIL_EXPIRATION": "1546327103738"
}


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

    def test_user_contact(self):
        result = train_api.user_contact(cookies=COOKIES)
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
