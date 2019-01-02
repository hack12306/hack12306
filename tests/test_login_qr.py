# encoding: utf8

import os
import time
import uuid
import json
import base64
from PIL import Image

from hack12306.api import TrainApi

def test_loin_qr():
    try:
        train_api = TrainApi()
        cookie_dict = train_api.auth_init()

        result = train_api.auth_qr_get(cookies=cookie_dict)
        assert isinstance(result, dict)
        qr_uuid = result['uuid']
        print 'qr uuid. %s' % qr_uuid
        qr_img_path = '/tmp/12306/login-qr-%s.jpeg' % uuid.uuid1().hex

        if not os.path.exists(os.path.dirname(qr_img_path)):
            os.makedirs(os.path.dirname(qr_img_path))

        with open(qr_img_path, 'wb') as f:
            f.write(base64.b64decode(result['image']))

        im = Image.open(qr_img_path)
        im.show()

        for _ in range(6):
            qr_check_result = train_api.auth_qr_check(qr_uuid, cookies=cookie_dict)
            print 'check qr result. %s' % json.dumps(qr_check_result, ensure_ascii=False)
            if qr_check_result['result_code'] == "2":
                print 'qr check success result. %s' % json.dumps(qr_check_result, ensure_ascii=False)
                break

            time.sleep(3)
        else:
            print 'scan qr login error and exit.'
            os._exists(-1)

        uamtk_result = train_api.auth_uamtk(qr_check_result['uamtk'], cookies=cookie_dict)
        print 'uamtk result. %s' % json.dumps(uamtk_result, ensure_ascii=False)

        uamauth_result = train_api.auth_uamauth(uamtk_result['newapptk'], cookies=cookie_dict)
        print 'uamauth result. %s' % json.dumps(uamauth_result, ensure_ascii=False)

        cookies = {
            'tk': uamauth_result['apptk']
        }
        cookies.update(**cookie_dict)
        user_info_result = train_api.user_info(cookies=cookies)
        print '%s login successfully.' % user_info_result['name']

    finally:
        if os.path.exists(qr_img_path):
            os.remove(qr_img_path)


if __name__ == '__main__':
    test_loin_qr()
