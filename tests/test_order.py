# encoding: utf8

"""
下单
"""

import json
import copy

from hack12306 import constants
from hack12306.order import TrainOrderAPI
from hack12306.query import TrainInfoQueryAPI
from hack12306.user import TrainUserAPI
from hack12306.utils import (tomorrow, JSONEncoder,
                             gen_old_passenge_tuple, gen_passenger_ticket_tuple)

from config import COOKIES

confirm_submit_order = False
seat_type = constants.SEAT_TYPE_SECONDE_SEAT
seat_type_code = dict(constants.SEAT_TYPE_CODE_MAP)[seat_type]
from_station = 'VNP'
to_station = 'SHH'


def test_order_no_complete():
    result = TrainOrderAPI().order_query_no_complete(cookies=COOKIES)
    print json.dumps(result, ensure_ascii=False)


def test_order():
    train_order_api = TrainOrderAPI()

    # 1. 查询剩余车票
    train_date = tomorrow().strftime('%Y-%m-%d')
    result = TrainInfoQueryAPI().info_query_left_tickets(train_date, from_station, to_station)
    train_info = None
    for train in result:
        if train[constants.SEAT_TYPE_SECONDE_SEAT]:
            train_info = copy.deepcopy(train)
            train_info.update(train_date=train_date)

    print 'query left tickets result. %s' % json.dumps(train_info, ensure_ascii=False)

    # 2. 下单-提交订单
    submit_order_result = train_order_api.order_submit_order(
        train_info['secret'],
        train_info['train_date'],
        cookies=COOKIES)
    print 'submit order result. %s' % submit_order_result

    # 3. 下单-确认乘客
    confirm_passenger_result = train_order_api.order_confirm_passenger(cookies=COOKIES)
    print 'confirm passenger result. %s' % json.dumps(confirm_passenger_result, ensure_ascii=False, cls=JSONEncoder)

    # 4. 下单-检查订单信息
    passengers = TrainUserAPI().user_passengers(cookies=COOKIES)
    passenger_info = passengers[0]
    passenger_ticket = gen_passenger_ticket_tuple(
        seat_type_code, passenger_info['passenger_flag'],
        passenger_info['passenger_type'],
        passenger_info['passenger_name'],
        passenger_info['passenger_id_type_code'],
        passenger_info['passenger_id_no'],
        passenger_info['mobile_no'])
    old_passenger = gen_old_passenge_tuple(passenger_info['passenger_name'], passenger_info['passenger_id_type_code'],
                                           passenger_info['passenger_id_no'], passenger_info['passenger_type'])

    passenger_ticket_str = ','.join(passenger_ticket)
    old_passenger_str = ','.join(old_passenger)
    check_order_result = train_order_api.order_confirm_passenger_check_order(
        confirm_passenger_result['token'],
        passenger_ticket_str, old_passenger_str, cookies=COOKIES)
    print 'check order result. %s' % json.dumps(check_order_result, ensure_ascii=False, cls=JSONEncoder)

    # 5. 下单-获取排队数量
    queue_count_result = train_order_api.order_confirm_passenger_get_queue_count(
        train_info['train_date'],
        train_info['train_num'],
        seat_type_code,
        train_info['from_station'],
        train_info['to_station'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['token'],
        confirm_passenger_result['order_request_params']['station_train_code'],
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['train_location'],
        cookies=COOKIES,
    )
    print 'confirm passenger get queue count result. %s' % json.dumps(queue_count_result, ensure_ascii=False, cls=JSONEncoder)

    if confirm_submit_order:
        # 6. 下单-确认车票
        confirm_ticket_result = train_order_api.order_confirm_passenger_confirm_single_for_queue(
            passenger_ticket_str, old_passenger_str,
            confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
            confirm_passenger_result['ticket_info']['key_check_isChange'],
            confirm_passenger_result['ticket_info']['leftTicketStr'],
            confirm_passenger_result['ticket_info']['train_location'],
            confirm_passenger_result['token'], cookies=COOKIES)
        print 'confirm passenger confirm ticket result. %s' % json.dumps(confirm_ticket_result, ensure_ascii=False, cls=JSONEncoder)

        # 7. 下单-查询订单
        query_order_result = train_order_api.order_confirm_passenger_query_order(confirm_passenger_result['token'])
        print 'confirm passenger query order result. %s' % json.dumps(query_order_result, ensure_ascii=False, cls=JSONEncoder)


if __name__ == '__main__':
    test_order()
