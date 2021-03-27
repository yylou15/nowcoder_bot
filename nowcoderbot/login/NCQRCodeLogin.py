import configparser
import json
import os
import time

import qrcode
import requests

from login.NCLogin import NCLogin


class NCQRCodeLogin(NCLogin):
    def do(self, session=None) -> requests.Session:
        if not session:
            session = requests.session()
        now = str(int(time.time()))
        code = json.loads(session.get("https://www.nowcoder.com/nccommon/scan/code?token=&_=" + now).text)['data'][
            'code']
        qr_data = "nowcoder-scan://code={}".format(code)
        # 实例化QRCode生成qr对象
        qr_code = qrcode.QRCode()
        # 传入数据
        qr_code.add_data(qr_data)
        qr_code.make(fit=True)
        # 生成二维码
        img = qr_code.make_image()
        # 展示二维码
        img.show()

        while True:
            scan_res = json.loads(
                session.get(
                    "https://www.nowcoder.com/nccommon/scan/updateInfo?token=&code={}&_={}".format(code, now)).text)
            if scan_res['code'] == 0:
                break
            time.sleep(1)

        return session

