# encoding: utf8

ORDER_COME_FROM_FLAG = (
    ('my_order', '全部'),
    ('my_resign', '可改签'),
    ('my_cs_resgin', '可变更到站'),
    ('my_refund', '可退款'),
)

ORDER_WHERE = (
    ('G', '未出行'),
    ('H', '历史订单'),
)

ORDER_QUERY_TYPE = (
    ('1', '按订票日期查询'),
    ('2', '按乘车日期查询'),
)

MEMBER_INFO_POINT_QUERY_TYPE = (
    ('0', '积分明细'),
    ('1', '收入明细'),
    ('2', '支出明细'),
)

SEAT_CATEGORY_BUSINESS_SEAT = 'business_seat'               # 商务座
SEAT_CATEGORY_FIRST_SEAT = 'first_seat'                     # 一等座
SEAT_CATEGORY_SECONDE_SEAT = 'second_seat'                  # 二等座
SEAT_CATEGORY_HIGH_SLEEPER_SEAT = 'high_soft_sleeper_seat'  # 高级软卧
SEAT_CATEGORY_SOFT_SLEEPER_SEAT = 'soft_sleeper_seat'       # 软卧
SEAT_CATEGORY_MOVING_SLEEPER_SEAT = 'moving_sleeper_seat'   # 动卧
SEAT_CATEGORY_HARD_SLEEPER_SEAT = 'hard_sleeper_seat'       # 硬卧
SEAT_CATEGORY_SOFT_SEAT = 'soft_seat'                       # 软座
SEAT_CATEGORY_HARD_SEAT = 'hard_seat'                       # 硬座
SEAT_CATEGORY_NO_SEAT = 'no_seat'                           # 无座
