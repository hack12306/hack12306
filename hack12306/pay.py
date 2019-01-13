# encoding: utf8
"""
pay.py
@author Meng.yangyang
@description Payment
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import re
import copy
import base64
import logging

import BeautifulSoup

from . import constants
from . import exceptions
from .base import TrainBaseAPI
from .auth import check_login

_logger = logging.getLogger('hack12306')

__all__ = ('TrainPayAPI',)


class TrainPayAPI(TrainBaseAPI):
    """
    支付
    """

    @check_login
    def pay_no_complete_order(self, sequence_no, arrive_time_str=None, pay_flag='pay', **kwargs):
        """
        支付-未完成订单
        :param sequence_no 订单号
        :param arrive_time_str
        :param pay_flag
        """
        url = "https://kyfw.12306.cn/otn/queryOrder/continuePayNoCompleteMyOrder"
        params = {
            'sequence_no': sequence_no,
            'pay_flag': pay_flag,
            'arrive_time_str': arrive_time_str or ''
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    def pay_init(self, **kwargs):
        """
        支付-订单支付初始化
        :return HTML
        """
        url = 'https://kyfw.12306.cn/otn/payOrder/init'

        resp = self.submit(url,method='GET', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        return resp.content

    @check_login
    def pay_check_new(self, **kwargs):
        """
        支付-发起支付
        :return JSON对象
        """
        def parse_form_tran_data(tran_data):
            xml_data = base64.b64decode(tran_data)

            # XML 解析失败，使用正则表达式代替
            interface_version_pattern = re.compile(r'<interfaceVersion>([0-9, \.]+)</interfaceVersion>')
            interface_version = interface_version_pattern.search(xml_data).group(1)

            interface_name_pattern = re.compile(r'<interfaceName>(.+)</interfaceName>')
            interface_name = interface_name_pattern.search(xml_data).group(1)

            order_date_pattern = re.compile(r'<orderDate>(.+)</orderDate>')
            order_date = order_date_pattern.search(xml_data).group(1)

            order_timeout_date_pattern = re.compile(r'<orderTimeoutDate>(.+)</orderTimeoutDate>')
            order_timeout_date = order_timeout_date_pattern.search(xml_data).group(1)

            order_id_pattern = re.compile(r'<orderId>(.+)</orderId>')
            order_id = order_id_pattern.search(xml_data).group(1)

            amount_pattern = re.compile(r'<amount>(\d+)</amount>')
            amount = amount_pattern.search(xml_data).group(1)

            app_id_pattern = re.compile(r'<appId>(\d+)</appId>')
            app_id = app_id_pattern.search(xml_data).group(1)

            cur_type_pattern = re.compile(r'<curType>(\d+)</curType>')
            cur_type = cur_type_pattern.search(xml_data).group(1)

            mer_url_pattern = re.compile(r'<merURL>(.+)</merURL>', re.DOTALL)
            mer_url = mer_url_pattern.search(xml_data).group(1)

            app_url_pattern = re.compile(r'<appURL>(.+)</appURL>', re.DOTALL)
            app_url = app_url_pattern.search(xml_data).group(1)

            inner_url_pattern = re.compile(r'<innerURL>(.+)</innerURL>', re.DOTALL)
            inner_url = inner_url_pattern.search(xml_data).group(1)

            mer_var_pattern = re.compile(r'<merVAR>(.+)</merVAR>', re.DOTALL)
            mer_var = mer_var_pattern.search(xml_data).group(1)

            trans_type_pattern = re.compile(r'<transType>(\d+)</transType>')
            trans_type = trans_type_pattern.search(xml_data).group(1)

            return {
                'interface_version': interface_version,
                'interface_name': interface_name,
                'order_date': order_date,
                'order_timeout_date': order_timeout_date,
                'order_id': order_id,
                'amount': amount,
                'app_id': app_id,
                'cur_type': cur_type,
                'mer_url': mer_url,
                'app_url': app_url,
                'inner_url': inner_url,
                'mer_var': mer_var,
                'trans_type': trans_type
            }

        url = 'https://kyfw.12306.cn/otn/payOrder/paycheckNew'
        params = {
            'batch_nos': kwargs.pop('batch_nos', ''),
            'coach_nos': kwargs.pop('coach_nos', ''),
            'seat_nos': kwargs.pop('seat_nos', ''),
            'passenger_id_types': kwargs.pop('passenger_id_types', ''),
            'passenger_id_nos': kwargs.pop('passenger_id_nos', ''),
            'passenger_names': kwargs.pop('passenger_names', ''),
            'insure_types': kwargs.pop('insure_types', ''),
            'if_buy_insure_only': kwargs.pop('if_buy_insure_only', 'N'),
            'hasBoughtIns': kwargs.pop('hasBoughtIns', ''),
            '_json_att': kwargs.pop('_json_att', '')
        }
        resp = self.submit(url, params, method="POST", **kwargs)

        data = copy.deepcopy(resp['data'])
        data['payForm']['tranDataParsed'] = parse_form_tran_data(data['payForm']['tranData'])
        return data

    @check_login
    def pay_gateway(self, trans_data, sign_msg, trans_type='01',  app_id='0001', interface_name='PAY_SERVLET', interface_version='PAY_SERVLET', **kwargs):
        """
        支付-收银台
        :param trans_data
        :param sign_msg
        :param trans_type
        :param app_id
        :param interface_name
        :param interface_version
        :return HTML
        """
        url = 'https://epay.12306.cn/pay/payGateway'
        params = {
            '_json_att': kwargs.pop('_json_att', ''),
            'interfaceName': interface_name,
            'interfaceVersion': interface_version,
            'tranData': trans_data,
            'merSignMsg': sign_msg,
            'appId': app_id,
            'transType': trans_type
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        # TODO 解析收银台 HTML 响应报文
        return resp.content

    @check_login
    def pay_web_business(self, tran_data, sign_msg, trans_type, custom_ip, order_timeout_date,
                         bank_id, channel_id='1', business_type="1", payment_type='0', app_id='0001', **kwargs):
        """
        支付-交易
        :param tran_data
        :param sign_msg
        :param trans_type
        :param channel_id
        :param custom_ip
        :param order_timeout_date
        :param bank_id
        :param business_type
        :param payment_type
        :param app_id
        """
        def parse_resp(content):
            params = []

            soup = BeautifulSoup.BeautifulSOAP(content)
            form = soup.find('form')

            form_attr_dict = dict(form.attrs)
            for e in form.findAll('input'):
                e_attr_dict = dict(e.attrs)
                params.append((e_attr_dict['name'], e_attr_dict['value']))

            return form_attr_dict['action'], form_attr_dict['method'].upper(), dict(params)

        url = 'https://epay.12306.cn/pay/webBusiness'
        params = {
            'tranData': tran_data,
            'transType': trans_type,
            'channelId': channel_id,
            'appId': app_id,
            'merSignMsg': sign_msg,
            'merCustomIp': custom_ip,
            'orderTimeoutDate': order_timeout_date,
            'paymentType': payment_type,
            'bankId': bank_id,
            'businessType': business_type
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        _logger.info('pay web business resp. status_code: %s content:%s' % (resp.status_code, resp.content))

        if resp.status_code != 200:
            raise exceptions.TrainRequestException(str(resp))

        failure_pattern = re.compile('交易失败')
        if failure_pattern.search(resp.content):
            raise exceptions.TrainAPIException(resp.content)

        url, method, params = parse_resp(resp.content)
        return {
            'url': url,
            'method': method,
            'params': params,
        }
