# encoding: utf8

import json
import pytest
from hack12306.api import TrainApi

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
    "JSESSIONID": "6E6B379091DCFB1D111B7675568B8AD1",
    "_jc_save_toStation": "%u798F%u5DDE%2CFZS",
    "tk": "QHGx4Hd_qFG-F8B-j9MlUMhVH4gj6f1gc4MLLglmh2h0",
    "_jc_save_czxxcx_fromDate": "2018-12-26",
    "RAIL_EXPIRATION": "1546327103738",
    "BIGipServerpassport": "904397066.50215.0000",
    "BIGipServerotn": "183501322.64545.0000",
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
        result = train_api.order_query('2018-11-30', '2018-12-29', cookies=COOKIES, query_where='G')
        assert isinstance(result, list)
        print json.dumps(result, ensure_ascii=False)

    def test_order_query_no_complete(self):
        result = train_api.order_query_no_complete(cookies=COOKIES)
        assert isinstance(result, list)
        print json.dumps(result)

