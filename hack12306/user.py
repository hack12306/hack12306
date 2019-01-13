# encoding: utf8

"""
user.py
@author Meng.yangyang
@description User and member info
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import re

from . import exceptions
from . import constants
from .base import TrainBaseAPI
from .auth import check_login

__all__ = ('TrainUserAPI', 'TrainMemberAPI',)


class TrainUserAPI(TrainBaseAPI):
    """
    用户
    """

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


class TrainMemberAPI(TrainBaseAPI):
    """
    会员中心
    """

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
