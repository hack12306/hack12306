# encoding: utf8

import re
import json
import logging
import requests
import collections

from . import settings
from . import constants
from . import exceptions
from .utils import urlencode

_logger = logging.getLogger('hack12306')

__all__ = ('TrainApi',)


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
            raise exceptions.TrainAPIException(content_json.get('errMsg', json.dumps(content_json, ensure_ascii=False)))

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
    def user_contact(self, **kwargs):
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
    def order_query(self, start_date, end_date, type='1', sequeue_train_name='', come_from_flag='my_order', query_where='G', **kwargs):
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
        assert come_from_flag in dict(constants.ORDER_COME_FROM_FLAG), 'invalid come_from_flag params. %s' % come_from_flag
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

    def info_query_left_tickets(self, train_date,  from_station, to_station, purpose_codes='ADULT', **kwargs):
        """
        信息查询-余票查询
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
        params = [
            ('leftTicketDTO.train_date', train_date),
            ('leftTicketDTO.from_station', from_station),
            ('leftTicketDTO.to_station',to_station),
            ('purpose_codes', purpose_codes),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' not in resp or 'result' not in resp['data']:
            return []

        trains = []
        for train_s in resp['data']['result']:
            train = train_s.split('|')
            trains.append({
                'remark': train[1],
                'train_num': train[2],
                'train_name': train[3],
                'from_station': train[4],
                'to_station': train[5],
                'departure_time': train[8],     # 出发时间
                'arrival_time': train[9],       # 到达时间
                'duration': train[10],          # 历时
                constants.SEAT_CATEGORY_BUSINESS_SEAT: train[32],
                constants.SEAT_CATEGORY_FIRST_SEAT: train[31],
                constants.SEAT_CATEGORY_SECONDE_SEAT: train[30],
                # constants.SEAT_CATEGORY_HIGH_SLEEPER_SEAT: '--',    # TODO 高级软卧
                constants.SEAT_CATEGORY_SOFT_SLEEPER_SEAT: train[23],
                constants.SEAT_CATEGORY_HARD_SLEEPER_SEAT: train[28],
                constants.SEAT_CATEGORY_SOFT_SEAT: train[24],
                constants.SEAT_CATEGORY_HARD_SEAT: train[29],
                constants.SEAT_CATEGORY_NO_SEAT: train[26],
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
        :return TODO
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
        assert query_type in dict(constants.MEMBER_INFO_POINT_QUERY_TYPE).keys(), 'Invalid query_type param. %s' % query_type
        assert isinstance(start_date, str) and date_pattern.match(start_date), 'Invalid start_date param. %s' % start_date
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
