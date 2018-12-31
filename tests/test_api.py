# encoding: utf8

import json
import pytest
import datetime
from hack12306.api import TrainApi
from hack12306.utils import tomorrow

train_api = TrainApi()

COOKIES = {
    "_jc_save_fromDate": "2018-12-24",
    "_jc_save_zwdch_cxlx": "0",
    "_jc_save_czxxcx_toStation": "%u5317%u4EAC%2CBJP",
    "RAIL_DEVICEID": "Dv9nY4_XzkbPhbA2wlkpuJ39PRw9LB-edng2VfjfYG3lcu6wKLR5PSF6LzzPc3WvbNuXVX_BN3R0ABFl6Ms_nccEBGM51kc6kg-XKryfTxtTv8_8pGXJxUfUXS8TcFEhQB_uvqNsfemB10Wjh4SdlCN-JAbEkb7E",
    "_jc_save_wfdc_flag": "dc",
    "route": "6f50b51faa11b987e576cdb301e545c4",
    "BIGipServerpool_passport": "216859146.50215.0000",
    "_jc_save_toDate": "2018-12-24",
    "JSESSIONID": "A860BC8176C9AF9D8D836769C933F328",
    "_jc_save_toStation": "%u798F%u5DDE%2CFZS",
    "tk": "G6mwDFb-QaU5hz8QMzz18NCeaP7gq6kcaiHP0wrwh2h0",
    "_jc_save_czxxcx_fromDate": "2018-12-26",
    "RAIL_EXPIRATION": "1546327103738",
    "BIGipServerpassport": "904397066.50215.0000",
    "BIGipServerotn": "233832970.64545.0000",
    "_jc_save_zwdch_fromStation": "%u5317%u4EAC%2CBJP",
    "_jc_save_fromStation": "%u6D77%u53E3%2CVUQ"
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
