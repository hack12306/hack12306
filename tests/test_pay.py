# encoding: utf8

"""
支付
"""

import os
import json
import copy
import platform
from hack12306 import constants
from hack12306.pay import TrainPayAPI
from hack12306.utils import tomorrow, JSONEncoder

from config import COOKIES, PUBLIC_IP_ADDR, ORDER_SEQUENCE_NO


def test_pay():
    train_pay_api = TrainPayAPI()

    # 1.支付未完成订单
    pay_no_complete_order_result = train_pay_api.pay_no_complete_order(ORDER_SEQUENCE_NO, cookies=COOKIES)
    print 'pay no complete order result. %s' % json.dumps(pay_no_complete_order_result, ensure_ascii=False,)

    # 2.支付初始化
    train_pay_api.pay_init(cookies=COOKIES)

    # 3.发起支付
    pay_check_new_result = train_pay_api.pay_check_new(cookies=COOKIES)
    print 'pay check new result. %s' % json.dumps(pay_check_new_result, ensure_ascii=False)

    pay_gateway_result = train_pay_api.pay_gateway(
        pay_check_new_result['payForm']['tranData'],
        pay_check_new_result['payForm']['merSignMsg'],
        cookies=COOKIES)

    # 4.交易
    pay_business_result = train_pay_api.pay_web_business(
        pay_check_new_result['payForm']['tranData'],
        pay_check_new_result['payForm']['merSignMsg'],
        pay_check_new_result['payForm']['transType'],
        PUBLIC_IP_ADDR, pay_check_new_result['payForm']['tranDataParsed']['order_timeout_date'],
        constants.BANK_ID_WX, cookies=COOKIES)
    print 'pay business result. %s' % json.dumps(pay_business_result, ensure_ascii=False)

    # 5.跳转第三方支付
    try:
        pay_filepath = '/tmp/12306/pay-%s-%s.html' % (constants.BANK_ID_WX, ORDER_SEQUENCE_NO)

        pay_business_third_pay_resp = train_pay_api.submit(
            pay_business_result['url'],
            pay_business_result['params'],
            method=pay_business_result['method'],
            parse_resp=False, cookies=COOKIES, allow_redirects=True)    # 如果希望第三方支付返回302重定向，设置allow_redirects=False
        print 'pay third resp status code. %s' % pay_business_third_pay_resp.status_code
        print 'pay third resp headers. location: %s' % pay_business_third_pay_resp.headers.get('Location', None)
        print 'pay third resp headers. %s' % json.dumps(pay_business_third_pay_resp.headers, ensure_ascii=False, cls=JSONEncoder)

        # 响应输出的文件，用浏览器打开
        if not os.path.exists(os.path.dirname(pay_filepath)):
            os.makedirs(os.path.dirname(pay_filepath))

        with open(pay_filepath, 'w') as f:
            f.write(pay_business_third_pay_resp.content)
    finally:
        if platform.mac_ver()[0]:
            # 浏览器打开支付页面
            os.system('open %s' % pay_filepath)
        else:
            if os.path.exists(pay_filepath):
                os.remove(pay_filepath)


if __name__ == '__main__':
    test_pay()
