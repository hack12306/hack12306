# encoding: utf8

import json
import pytest
from hack12306.api import TrainApi

train_api = TrainApi()

COOKIES = {
    "_jc_save_fromDate": "2018-12-24",
    "_jc_save_czxxcx_toStation": "%u5317%u4EAC%2CBJP",
    "_jc_save_zwdch_cxlx": "0",
    "BIGipServerpool_passport": "283968010.50215.0000",
    "_jc_save_wfdc_flag": "dc",
    "route": "9036359bb8a8a461c164a04f8f50b252",
    "RAIL_DEVICEID": "Dv9nY4_XzkbPhbA2wlkpuJ39PRw9LB-edng2VfjfYG3lcu6wKLR5PSF6LzzPc3WvbNuXVX_BN3R0ABFl6Ms_nccEBGM51kc6kg-XKryfTxtTv8_8pGXJxUfUXS8TcFEhQB_uvqNsfemB10Wjh4SdlCN-JAbEkb7E",
    "_jc_save_toDate": "2018-12-24",
    "JSESSIONID": "25AD2C809D9B4D332660439C13EAB2BE",
    "_jc_save_fromStation": "%u6D77%u53E3%2CVUQ",
    "_jc_save_toStation": "%u798F%u5DDE%2CFZS",
    "BIGipServeropn": "1492124170.38945.0000",
    "tk": "EX-yKD2MKlQG_Q9GXRWsjy9MtM57Yszuay6V6gy0h2h0",
    "_jc_save_czxxcx_fromDate": "2018-12-26",
    "RAIL_EXPIRATION": "1546327103738",
    "current_captcha_type": "C",
    "_jc_save_zwdch_fromStation": "%u5317%u4EAC%2CBJP",
    "BIGipServerotn": "686817802.24610.0000"
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
