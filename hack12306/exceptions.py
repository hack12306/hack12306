# encoding: utf8


class TrainBaseException(Exception):
    """
    12306异常
    """


class TrainAPIException(TrainBaseException):
    """
    12306 API 异常
    """

class TrainUserNotLogin(TrainAPIException):
    """
    用户未登录
    """