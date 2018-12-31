# encoding: utf8

import re
import json
import logging
import requests

from . import settings
from . import constants
from . import exceptions

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

        args[0].user_check_login(**kwargs)
        return f(*args, **kwargs)

    return wrapper


class TrainApi(object):
    """
    12306 Train API.
    """

    def submit(self, url, params=None, method='POST', format='form', **kwargs):
        _logger.debug('train request. url:%s method:%s params:%s' % (url, method, json.dumps(params)))

        if method == 'GET':
            resp = requests.get(url, params, **kwargs)
        elif method == 'POST':
            if format == 'json':
                resp = requests.post(url, json=params, **kwargs)
            else:
                resp = requests.post(url, data=params, **kwargs)
        else:
            assert False, 'Unknown http method'

        if resp.status_code != 200:
            raise exceptions.TrainAPIException()

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
            raise exceptions.TrainAPIException('response is not valid json type')

        if content_json['status'] is not True:
            raise exceptions.TrainAPIException(content_json['errMsg'])

        return content_json

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
        return resp['data']['normal_passengers']

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
