# -*- coding: utf-8 -*-
import requests
import base64
from core.storage import config
from core.log import logger


class OCR:
    def __init__(self):
        self.access_token = self.get_access_token(config.ocr['api-key'], config.ocr['secret-key'])

    @staticmethod
    def get_access_token(ak, sk):
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s' % (
            ak, sk)
        response = requests.get(host)
        j = response.json()
        return j['access_token']

    def number_from_file(self, filepath: str):
        """
        数字识别
        """
        # 二进制方式打开图片文件
        try:
            f = open(filepath, 'rb')
            return self.number_from_bytes(f.read())
        except Exception as e:
            logger.warning("failed to open the file: " + str(e))
            return None

    def number_from_bytes(self, img_bin: bytes):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
        img_b64 = base64.b64encode(img_bin)
        params = {"image": img_b64}
        request_url = request_url + "?access_token=" + self.access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        try:
            j = response.json()
            c = j['words_result'][0]['words']
            logger.debug("checkcode is {}".format(c))
            return c
        except:
            return None


# debug
if __name__ == '__main__':
    ocr = OCR()
    print(ocr.number_from_file("tmp/checkcode.php"))
