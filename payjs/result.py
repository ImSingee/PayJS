import logging
from pprint import pformat

logger = logging.getLogger(__name__)


class PayJSResultBase:
    def __init__(self, raw_response, r_json: dict = None):
        self.raw_response = raw_response  # 原始 requests.Response 数据
        self.content = raw_response.content  # 原始 response 的 content
        self.url = raw_response.url  # 请求的 url
        self.STATUS_CODE = raw_response.status_code  # HTTP 请求返回的状态吗
        self.json = r_json  # 请求返回的内容包装后的 JSON 值（以 dict 存储或为 None/False）
        self.JSON = self.json

    def __repr__(self):
        d = self.__dict__.copy()
        for m in ('key', 'content', 'raw_response', 'ERROR', 'JSON', 'ERROR_MSG'):
            try:
                d.pop(m)
            except KeyError:
                continue
        return pformat(d)


class PayJSResultSuccess(PayJSResultBase):
    def __bool__(self):
        return True

    def __init__(self, raw_response, **kwargs):
        super(PayJSResultSuccess, self).__init__(raw_response=raw_response, **kwargs)

        if type(self.json) is dict:
            for k, v in self.json.items():
                if k not in ['sign']:
                    setattr(self, k, v)

        if '/api/check' in self.url:
            self.PAID = True if getattr(self, 'status') == 1 else False  # 是否已支付
            self.paid = self.PAID
        if '/api/cashier' in self.url:
            self.REDIRECT = raw_response.headers.get('Location')
            self.redirect = self.REDIRECT


class PayJSResultFail(PayJSResultBase):
    ERROR_NO = 0

    def __bool__(self):
        return False

    def __init__(self, raw_response, **kwargs):
        super().__init__(raw_response=raw_response, **kwargs)
        if not self.json:
            self.error_msg = '请求失败'  # 错误信息
        else:
            self.error_msg = self.json.get('msg') or self.json.get('return_msg')
