# encoding: utf8
"""
exceptions.py
@author Meng.yangyang
@description Exception
@created Wed Dec 26 2018 23:41:08 GMT+0800 (CST)
"""

class TrainBaseException(Exception):
    """
    12306异常
    """


class TrainRequestException(TrainBaseException):
    """
    12306请求异常
    """


class TrainAPIException(TrainBaseException):
    """
    12306 API 异常
    """

class TrainUserNotLogin(TrainAPIException):
    """
    用户未登录
    """