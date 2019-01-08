"""
exceptions.py
@author Meng.yangyang
@description 异常
@created Wed Dec 26 2018 23:41:08 GMT+0800 (CST)
@last-modified Tue Jan 08 2019 18:30:11 GMT+0800 (CST)
"""

# encoding: utf8


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