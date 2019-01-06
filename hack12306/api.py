# encoding: utf8

import re
import copy
import time
import json
import base64
import urllib
import logging
import datetime
import requests
import collections
import BeautifulSoup

from . import settings
from . import constants
from . import exceptions
from .utils import urlencode, tomorrow, time_cst_format

_logger = logging.getLogger('hack12306')

__all__ = ('TrainApi', 'gen_passenger_ticket_tuple', 'gen_old_passenge_tuple',)


def gen_passenger_ticket_tuple(seat_type, passenger_flag, passenge_type, name, id_type, id_no, mobile, **kwargs):
    l = [seat_type, passenger_flag, passenge_type, name, id_type, id_no, mobile, 'N']
    return tuple([unicode(i).encode('utf8') for i in l])


def gen_old_passenge_tuple(name, id_type, id_no, **kwargs):
    l = [name, id_type, id_no, '1_']
    return tuple([unicode(i).encode('utf8') for i in l])


def check_login(f):
    """
    用户登录检查装饰器
    """

    def wrapper(*args, **kwargs):
        assert isinstance(args[0], TrainApi), 'decorated function must be TrainApi method'
        cookies = kwargs.get('cookies', None)
        if not cookies:
            raise exceptions.TrainUserNotLogin()

        if not args[0].user_check_login(**kwargs):
            raise exceptions.TrainUserNotLogin()

        return f(*args, **kwargs)

    return wrapper


class TrainApi(object):

    """
    12306 Train API.
    """

    def submit(self, url, params=None, method='POST', format='form', parse_resp=True, **kwargs):
        _logger.debug('train request. url:%s method:%s params:%s' % (url, method, json.dumps(params)))

        if method == 'GET':
            if isinstance(params, list):
                params = urlencode(params)
            resp = requests.get(url, params, **kwargs)
        elif method == 'POST':
            if format == 'json':
                resp = requests.post(url, json=params, **kwargs)
            else:
                resp = requests.post(url, data=params, **kwargs)
        else:
            assert False, 'Unknown http method'

        if not parse_resp:
            return resp

        if resp.status_code != 200:
            raise exceptions.TrainRequestException(str(resp))

        try:
            content_json = json.loads(resp.content)
        except ValueError as e:
            if settings.DEBUG:
                import os
                import uuid
                import datetime

                today_str = datetime.date.today().strftime('%Y-%m-%d')
                filepath = '/tmp/hack12306/%s/%s-%s' % (today_str, url, uuid.uuid1().hex)
                if not os.path.exists(os.path.dirname(filepath)):
                    os.makedirs(os.path.dirname(filepath))

                with open(filepath, 'w') as f:
                    f.write(resp.content)

            _logger.warning(e)
            raise exceptions.TrainRequestException('response is not valid json type')

        if content_json['status'] is not True:
            _logger.warning('%s resp. %s' % (url, resp.content))
            raise exceptions.TrainAPIException(resp.content)

        return content_json

    def auth_init(self, **kwargs):
        """
        认证-初始化，获取 cookies 信息
        :return JSON DICT
        """
        route_pattern = re.compile(r'route=[0-9, a-z]*;')
        jsessionid_pattern = re.compile(r'JSESSIONID=[0-9, a-z, A-Z]*;')
        bigipserverotn_pattern = re.compile(r'BIGipServerotn=[0-9, \.]*;')

        url = 'https://kyfw.12306.cn/otn/login/conf'
        resp = self.submit(url, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        cookie_str = resp.headers['Set-Cookie']
        cookie_dict = {
            'route': route_pattern.search(cookie_str).group().split('=')[1].strip(';'),
            'JSESSIONID': jsessionid_pattern.search(cookie_str).group().split('=')[1].strip(';'),
            'BIGipServerotn': bigipserverotn_pattern.search(cookie_str).group().split('=')[1].strip(';'),
        }
        return cookie_dict

    def auth_qr_get(self, **kwargs):
        """
        认证-获取登录二维码
        :return JSON对象
        """
        url = 'https://kyfw.12306.cn/passport/web/create-qr64'
        params = {
            'appid': 'otn'
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException(str(resp))
        return json.loads(resp.content)

    def auth_qr_check(self, uuid, **kwargs):
        """
        认证-检查二维码是否登录
        :param uuid 获取二维码请求中返回的 UUID
        :return COOKIES JSON 对象
        """
        assert isinstance(uuid, (str, unicode))

        url = 'https://kyfw.12306.cn/passport/web/checkqr'
        params = {
            'uuid': uuid,
            'appid': 'otn',
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        return json.loads(resp.content)

    def auth_uamtk(self, uamtk, **kwargs):
        """
        认证-UAM流票
        :param uamtk 流票
        :return JSON 对象
        """
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        params = {
            'uamtk': uamtk,
            'appid': 'otn',
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        return json.loads(resp.content)

    def auth_uamauth(self, apptk, **kwargs):
        """
        认证-UAM认证
        :param apptk
        :return TODO
        """
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        params = {
            'tk': apptk
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()
        return json.loads(resp.content)

    def credit_query_dishonest(self, **kwargs):
        """
        信用信息-失信已执行名单
        :return JSON对象
        """
        url = 'https://dynamic.12306.cn/otn/queryDishonest/query'
        resp = self.submit(url, method='GET')
        return resp['data']['right']

    def user_check_login(self, cookies=None, **kwargs):
        """
        用户-检查是否登录
        :params cookies: 用户 Session 信息
        :return True:已登录 False:未登录
        """
        if not cookies:
            return False

        assert isinstance(cookies, dict)

        url = 'https://kyfw.12306.cn/otn/login/conf'
        resp = self.submit(url, method='POST', cookies=cookies)
        if resp['data']['is_login'] == 'Y':
            return True
        else:
            return False

    @check_login
    def user_info(self, **kwargs):
        """
        用户-个人信息
        :return JSON对象
        """

        url = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfoApi'
        resp = self.submit(url, **kwargs)

        resp_data = resp['data']
        user = resp['data']['userDTO']
        login_user = resp['data']['userDTO']['loginUserDTO']
        result = {
            'user_type_name': resp_data['userTypeName'],
            'pic_flag': resp_data['picFlag'],
            'can_upload': resp_data['canUpload'],
            'user_password': resp_data['userPassword'],
            'is_mobile_check': resp_data['isMobileCheck'],
            'country_name': resp_data['country_name'],
            'user_name': login_user['user_name'],
            'name': login_user['name'],
            'id_type_code': login_user['id_type_code'],
            'id_type_name': login_user['id_type_name'],
            'id_no': login_user['id_no'],
            'member_id': login_user['member_id'],
            'member_level': login_user['member_level'],
            'country_code': user['country_code'],
            'sex': user['sex_code'],
            'mobile_no': user['mobile_no'],
            'email': user['email'],
            'address': user['address'],
            'is_active': user['is_active'],
            'user_id': user['user_id'],
            'user_status': user['user_status'],
            'is_valid': user['is_valid'],
            'need_modify_email': user['needModifyEmail'],
            'birthday': resp_data['bornDateString'],
        }
        return result

    @check_login
    def user_passengers(self, **kwargs):
        """
        用户-常用联系人信息
        :return JSON LIST
        """
        url = 'http://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        resp = self.submit(url, method='POST', **kwargs)
        if 'data' in resp and 'normal_passengers' in resp['data']:
            return resp['data']['normal_passengers']
        else:
            return []

    @check_login
    def user_addresses(self, **kwargs):
        """
        用户-地址
        :return JSON LIST
        """
        url = 'https://kyfw.12306.cn/otn/address/initApi'
        resp = self.submit(url, method='POST', **kwargs)
        return resp['data']['addresses']

    @check_login
    def order_submit_order(self, secret_str, train_date, query_from_station_name=None, query_to_station_name=None,
                           purpose_codes='ADULT', tour_flag='dc', back_train_date=None, undefined=None,
                           **kwargs):
        """
        订单-下单-提交订单
        :param secret_str
        :param train_date 乘车日期
        :param back_train_date 返程日期
        :param tour_flag
        :param purpose_codes 默认为“ADULT”
        :param query_from_station_name 查询车站名称
        :param query_to_station_name 查询到站名称
        :return Boolean True-成功  False-失败
        """
        date_pattern = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        if back_train_date:
            assert date_pattern.match(back_train_date), 'Invalid back_train_date param. %s' % back_train_date
        else:
            back_train_date = tomorrow().strftime('%Y-%m-%d')

        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        params = {
            'secretStr': urllib.unquote(secret_str),
            'train_date': train_date,
            'back_train_date': back_train_date,
            'tour_flag': tour_flag,
            'purpose_codes': purpose_codes,
            'query_from_station_name': query_from_station_name or '',
            'query_to_station_name': query_to_station_name or '',
            'undefined': undefined or ''
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        if resp['httpstatus'] == 200 and resp['status'] is True:
            return True
        else:
            raise exceptions.TrainAPIException('submit order error. %s' % json.dumps(resp, ensure_ascii=False))

    @check_login
    def order_confirm_passenger(self, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客初始化
        :param _json_att
        :return JSON 对象
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        params = {
            '_json_att': _json_att or ''
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        token_pattern = re.compile(r"var globalRepeatSubmitToken = '(\S+)'")
        token = token_pattern.search(resp.content).group(1)

        ticket_info_pattern = re.compile(r'var ticketInfoForPassengerForm=(\{.+\})?')
        ticket_info = json.loads(ticket_info_pattern.search(resp.content).group(1).replace("'", '"'))

        order_request_params_pattern = re.compile(r'var orderRequestDTO=(\{.+\})?')
        order_request_params = json.loads(order_request_params_pattern.search(resp.content).group(1).replace("'", '"'))

        resp = {
            'token': token,
            'ticket_info': ticket_info,
            'order_request_params': order_request_params,
        }
        return resp

    @check_login
    def order_confirm_passenger_check_order(self, token, passenger_ticket, old_passenger, tour_flag='dc',
                                            cancel_flag=2, bed_level_order_num='000000000000000000000000000000',
                                            whatsSelect=1, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，检查订单
        :param cancel_flag
        :param bed_level_order_num
        :param passenger_ticket
        :param old_passenger
        :param tour_flag
        :param whatsSelect
        :param _json_att
        :param token
        :return JSON 对象
        """
        assert isinstance(passenger_ticket, tuple), 'Invalid passenger_ticket_tuple param. %s' % passenger_ticket
        assert isinstance(old_passenger, tuple), 'Invalid old_passenger_tuple param. %s' % old_passenger

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        params = {
            'cancel_flag': cancel_flag,
            'bed_level_order_num': bed_level_order_num,
            'passengerTicketStr': ','.join(passenger_ticket),
            'oldPassengerStr': ','.join(old_passenger),
            'tour_flag': tour_flag,
            'randCode': '',
            'whatsSelect': whatsSelect,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }

        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_get_queue_count(self, train_date, train_no, seat_type,
                                                from_station_telecode, to_station_telecode, left_ticket,
                                                token, station_train_code, purpose_codes, train_location,
                                                _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，获取排队数量
        :param train_date CST格式时间
        :param train_no
        :param seat_type 席别
        :param from_station_telecode 出发站编码
        :param to_station_telecode 到站编码
        :param left_ticket
        :param token
        :param station_train_code
        :param purpose_codes
        :param train_location
        :param _json_att
        :return JSON 对象
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date
        train_date = time_cst_format(datetime.datetime.strptime(train_date, '%Y-%m-%d'))

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        params = {
            'train_date': train_date,
            'train_no': train_no,
            'stationTrainCode': station_train_code,
            'seatType': seat_type,
            'fromStationTelecode': from_station_telecode,
            'toStationTelecode': to_station_telecode,
            'leftTicket': left_ticket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_confirm_single_for_queue(self, passenger_ticket, old_passenger, purpose_codes,
                                                         key_check_isChange, left_ticket, train_location,
                                                         token, whats_select='1', dw_all='N', room_type=None, 
                                                         seat_detail_type=None, choose_seats=None, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，确认车票
        :param passenger_ticket
        :param old_passenger
        :param purpose_codes
        :param key_check_isChange
        :param left_ticket
        :param train_location
        :param choose_seats
        :param seat_detail_type
        :param whats_select
        :param root_type
        :param dw_all
        :param _json_att
        :param token
        :return TODO
        """
        assert isinstance(passenger_ticket, (list, tuple)), 'Invalid passenger_ticket param. %s' % passenger_ticket
        assert isinstance(old_passenger, (list, tuple)), 'Invalid old_passenger param. %s'  % old_passenger


        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        params = {
            'passengerTicketStr': passenger_ticket,
            'oldPassengerStr':  old_passenger,
            'randCode': '',
            'purpose_codes': purpose_codes,
            'key_check_isChange': key_check_isChange,
            'leftTicketStr': left_ticket,
            'train_location': train_location,
            'choose_seats': choose_seats or '',
            'seatDetailType': seat_detail_type,
            'whatsSelect': whats_select,
            'roomType': room_type,
            'dwAll': dw_all,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp

    @check_login
    def order_confirm_passenger_query_order(self, token, tour_flag='dc', random=None, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，查询
        :param random
        :pram tour_flag
        :pram token
        :pram _json_att
        """
        random = random or str(int(time.time()*100))

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        params = [
            ('random', random),
            ('tourFlag', tour_flag),
            ('_json_att', _json_att or ''),
            ('REPEAT_SUBMIT_TOKEN', token),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        return resp

    @check_login
    def order_confirm_passenger_result_order(self, sequence_no, token, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，订单结果
        :pram senquence_no
        :param _json_att
        :param token
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        params = {
            'orderSequence_no': sequence_no,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        resp = self.submit(url, params, method="POST", **kwargs)
        return resp

    @check_login
    def order_query(self, start_date, end_date, type='1', sequeue_train_name='',
                    come_from_flag='my_order', query_where='G', **kwargs):
        """
        订单-查询
        :param start_date 开始日期，格式YYYY-mm-dd
        :param end_date 结束日期，格式 YYYY-mm-dd
        :param type 查询类型 "1"-按订票日期查询，"2"-按乘车日期查询
        :param sequeue_train_name 订单号，车次，姓名
        :param come_from_flag 来源标志 “my_order”-全部，“my_resign”-可改签，“my_cs_resgin”-可变更到站，“my_refund”-可退款
        :param query_where 订单来源 "G"-未出行，"H"-历史订单
        :return JSON LIST
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

        assert date_pattern.match(start_date), 'invalid start_date params. %s' % start_date
        assert date_pattern.match(end_date), 'invalid end_date params. %s' % end_date
        assert type in dict(constants.ORDER_QUERY_TYPE), 'invalid type params. %s' % type
        assert come_from_flag in dict(
            constants.ORDER_COME_FROM_FLAG), 'invalid come_from_flag params. %s' % come_from_flag
        assert query_where in dict(constants.ORDER_WHERE), 'invalid query_where params. %s' % query_where

        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'
        params = {
            'come_from_flag': come_from_flag,
            'query_where': query_where,
            'queryStartDate': start_date,
            'queryEndDate': end_date,
            'queryType': type,
            'sequence_train_name': sequeue_train_name or '',
            'pageIndex': kwargs.get('page_offset', 0),
            'pageSize': kwargs.get('page_size', 8),
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        if 'data' in resp and 'OrderDTODataList' in resp['data']:
            return resp['data']['OrderDTODataList']
        else:
            return []

    @check_login
    def order_query_no_complete(self, **kwargs):
        """
        订单-未完成订单
        """
        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
        resp = self.submit(url, method='POST', **kwargs)
        if 'data' in resp and 'OrderDTODataList' in resp['data']:
            return resp['data']['OrderDTODataList']
        else:
            return []

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
        if resp.status_code != 200:
            raise exceptions.TrainRequestException(str(resp))
''
        url, method, params = parse_resp(resp.content)
        return {
            'url': url,
            'method': method,
            'params': params,
        }

    def info_query_left_tickets(self, train_date,  from_station, to_station, purpose_codes='ADULT', **kwargs):
        """
        信息查询-余票查询
        :param train_date 乘车日期
        :param from_station 出发站
        :param to_station 到达站
        :return JSON 数组
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
        params = [
            ('leftTicketDTO.train_date', train_date),
            ('leftTicketDTO.from_station', from_station),
            ('leftTicketDTO.to_station', to_station),
            ('purpose_codes', purpose_codes),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' not in resp or 'result' not in resp['data']:
            return []

        trains = []
        for train_s in resp['data']['result']:
            train = train_s.split('|')
            trains.append({
                'secret': train[0],
                'remark': train[1],
                'train_num': train[2],
                'train_name': train[3],
                'from_station': train[4],
                'to_station': train[5],
                'departure_time': train[8],     # 出发时间
                'arrival_time': train[9],       # 到达时间
                'duration': train[10],          # 历时
                constants.SEAT_TYPE_BUSINESS_SEAT: train[32],
                constants.SEAT_TYPE_FIRST_SEAT: train[31],
                constants.SEAT_TYPE_SECONDE_SEAT: train[30],
                # constants.SEAT_TYPE_HIGH_SLEEPER_SEAT: '--',    # TODO 高级软卧
                constants.SEAT_TYPE_SOFT_SLEEPER_SEAT: train[23],
                constants.SEAT_TYPE_HARD_SLEEPER_SEAT: train[28],
                constants.SEAT_TYPE_SOFT_SEAT: train[24],
                constants.SEAT_TYPE_HARD_SEAT: train[29],
                constants.SEAT_TYPE_NO_SEAT: train[26],
            })
        return trains

    def info_query_station_trains(self, train_start_date, train_station_code, **kwargs):
        """
        信息查询-车站(车次)查询
        :param train_start_date 开始日期
        :param train_station_code 车站编码
        :return JSON LIST
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_start_date), 'Invalid train_start_date param. %s' % train_start_date

        url = 'https://kyfw.12306.cn/otn/czxx/query'
        params = {
            'train_start_date': train_start_date,
            'train_station_code': train_station_code
        }
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp and 'data' in resp['data']:
            return resp['data']['data']

    def info_query_train_no(self, train_no, from_station_telecode, to_station_telecode, depart_date, **kwargs):
        """
        信息查询-车次查询
        :param train_no 车次号
        :param from_station_telecode 起始车站编码
        :param to_station_telecode 到站车站编码
        :param depart_date 乘车日期
        :return JSON DICT
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(depart_date), 'Invalid depart_date param. %s' % depart_date

        url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo'
        params = [
            ('train_no', train_no),
            ('from_station_telecode', from_station_telecode),
            ('to_station_telecode', to_station_telecode),
            ('depart_date', depart_date),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp and 'data' in resp['data']:
            return resp['data']['data']
        else:
            return []

    def info_query_ticket_price(self, train_no, from_station_no, to_station_no, seat_types, train_date, **kwargs):
        """
        信息查询-车票价格
        :param train_no 车次号
        :param from_station_no 始发站
        :param to_station_no 到站
        :param seat_types 席别
        :param train_date 日期
        :return JSON DICT
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        # TODO 席别枚举检查

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'
        params = [
            ('train_no', train_no),
            ('from_station_no', from_station_no),
            ('to_station_no', to_station_no),
            ('seat_types', seat_types),
            ('train_date', train_date)
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp:
            return resp['data']
        else:
            return {}

    def info_query_station_list(self, station_version=None, **kwargs):
        """
        信息查询-车站列表
        :param station_version 版本号
        :return JSON 数组
        """
        def _parse_stations(s):
            station_list = []

            s = s.replace(';', '')
            s = s.replace('var station_names =', '')

            s_list = s.split('@')
            s_list.pop(0)

            for station in s_list:
                station_tuple = tuple(station.split('|'))
                station_list.append({
                    'name': station_tuple[1],
                    'short_name': station_tuple[0],
                    'code': station_tuple[2],
                    'english_name': station_tuple[3],
                    'index': station_tuple[5]
                })
            return station_list

        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        params = {
            'station_version': station_version or '',
        }
        resp = self.submit(url, params, method='GET', parse_resp=False, **kwargs)
        if not resp.status_code == 200:
            raise exceptions.TrainAPIException(str(resp))

        return _parse_stations(resp.content)

    def info_query_station_by_name(self, station_name, station_version=None, **kwargs):
        station_list = self.info_query_station_list(station_version)
        for station in station_list:
            if station['name'] == station_name:
                return station
        else:
            return None

    @check_login
    def member_info_query_member(self, **kwargs):
        """
        会员中心-查询信息
        :return JSON DICT
        """
        url = 'https://cx.12306.cn/tlcx/memberInfo/queryMemberIntegration'
        resp = self.submit(url, method='POST', **kwargs)
        if 'data' in resp:
            return resp['data']
        else:
            return {}

    @check_login
    def member_info_query_member_point(self, **kwargs):
        """
        会员中心-查询会员等级
        :return JSON DICT
        """
        url = 'https://cx.12306.cn/tlcx/memberInfo/memberPointQuery'
        resp = self.submit(url, method='POST', **kwargs)
        if 'data' in resp:
            return resp['data']
        else:
            return {}

    @check_login
    def member_info_query_point_history(self, query_type, start_date, end_date, page_index=1, page_size=10, **kwargs):
        """
        会员中心-查询积分记录
        :return TODO
        """
        date_pattern = re.compile('^[0-9]{4}[0-9]{2}[0-9]{2}$')
        assert query_type in dict(
            constants.MEMBER_INFO_POINT_QUERY_TYPE).keys(), 'Invalid query_type param. %s' % query_type
        assert isinstance(start_date, str) and date_pattern.match(
            start_date), 'Invalid start_date param. %s' % start_date
        assert isinstance(end_date, str) and date_pattern.match(end_date), 'Invalid end_date param. %s' % end_date

        url = 'https://cx.12306.cn/tlcx/memberInfo/pointSimpleQuery'
        params = [
            ('queryType', query_type),
            ('queryStartDate', start_date),
            ('queryEndDate', end_date),
            ('pageIndex', page_index),
            ('pageSize', page_size),
        ]
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp
