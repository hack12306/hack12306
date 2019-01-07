# encoding: utf8

import re

from . import constants
from . import exceptions
from .base import TrainBaseAPI

__all__ = ('TrainInfoQueryAPI',)


class TrainInfoQueryAPI(TrainBaseAPI):
    """
    信息查询
    """

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
