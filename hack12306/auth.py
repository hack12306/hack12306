# encoding: utf8
"""
auth.py
@author Meng.yangyang
@description Authentication
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import re
import json

from .base import TrainBaseAPI
from . import exceptions

__all__ = ('TrainAuthAPI', 'check_login',)


class TrainAuthAPI(TrainBaseAPI):
    """
    认证
    """

    def auth_check_login(self, cookies=None, **kwargs):
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


def check_login(f):
    """
    用户登录检查装饰器
    """

    def wrapper(*args, **kwargs):
        assert isinstance(args[0], TrainBaseAPI), 'decorated function must be TrainBaseAPI method'
        cookies = kwargs.get('cookies', None)
        if not cookies:
            raise exceptions.TrainUserNotLogin()

        if not TrainAuthAPI().auth_check_login(**kwargs):
            raise exceptions.TrainUserNotLogin()

        return f(*args, **kwargs)

    return wrapper
