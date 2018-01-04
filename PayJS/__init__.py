import re
import requests
import json
from hashlib import md5
from pprint import pformat
from urllib.parse import urlencode, unquote_plus


class PayJS:
    """
    PayJS
    用于 payjs.cn 的 API
    """

    FORCE_SSL = True

    payjs_order_id = ''

    def __init__(self, mchid: str, key: str, notify_url=None, **kwargs):
        """
        初始化

        :param mchid: 商户号
        :param key: 密钥
        :param notify_url: （可选）异步通知的 URL，留空为不通知或在发起请求时设置
        :param FORCE_SSL: （默认为 True）回调地址强制使用 HTTPS
        """

        for k, v in kwargs.items():
            self.__setattr__(k, v)

        if type(mchid) is not str:
            raise ValueError("商户号格式必须为字符串")
        if len(mchid) != 6:
            raise ValueError("商户号必须为六位")

        self.mchid = mchid

        if type(key) is not str:
            raise ValueError("密钥格式必须为字符串")
        if len(key) != 16:
            raise ValueError("密钥必须为十六位")

        self.key = key

        if not self.check_url(notify_url):
            raise ValueError("通知回调网址错误")

        self.notify_url = notify_url

    def sign(self, data: dict):
        """
        签名过程如下：
        0. 忽略已经存在的 sign
        1. 将所有参数名按照字典序排列，并以 "参数1=值1&参数2=值2&参数3=值3" 的形式排序
        2. 将上面的内容加上 "&key=KEY"（KEY 为设置的商户密钥）
        3. 将组合后的字符串转换为大写 MD5

        :param data: 要签名的参数字典
        :return: 签名后的字符串
        :rtype: str
        """
        d = data.copy()
        try:
            d.pop('sign')
        except KeyError:
            pass
        p = sorted([x for x in d.items() if (x[1] or x[1] == 0)], key=lambda x: x[0])
        p.append(('key', self.key))

        p = unquote_plus(urlencode(p))

        h = md5()
        h.update(p.encode())

        r = h.hexdigest().upper()

        return r

    def request(self, url: str, data: dict):
        """
        处理请求（请求时会过滤值为空的参数）

        :param url: 请求的 url
        :param data: 请求的参数字典（不包含签名）
        :return: 返回一个 PayJSResultSuccess 或 PayJSResultFail 类元素
        """
        data['sign'] = self.sign(data)
        data = {k: v for k, v in data.items() if v}
        r = requests.post(url, data=data, allow_redirects=False)
        return self.parse_response(r)

    def parse_response(self, response: requests.Response):
        """
        处理请求，将 requests 的返回包装为 PayJSResult
        :param response: requests 的返回值
        :return: 一个 PayJSResult 元素（Success 或 Fail）
        """
        if response.status_code == 200:
            # 扫码支付 与 订单查询；收银台支付失败
            try:
                j = json.loads(response.content)
            except json.JSONDecodeError:
                return PayJSResultFail(base=self, raw_response=response, r_json=False)
            except UnicodeDecodeError:
                return PayJSResultFail(base=self, raw_response=response, r_json=False)

            if str(j.get('return_code')) == '0':  # 请求失败
                response = PayJSResultFail(base=self, raw_response=response, r_json=j)
            else:
                if self.sign(j) == j.get('sign'):
                    response = PayJSResultSuccess(base=self, raw_response=response, r_json=j)
                else:
                    response = PayJSResultFail(base=self, raw_response=response, r_json=j)
                    response.ERROR_MSG = '返回的签名错误'

        elif response.status_code == 302:
            # 收银台支付
            return PayJSResultSuccess(base=self, raw_response=response, r_json=None)
        else:
            response = PayJSResultFail(base=self, raw_response=response, r_json=False)
        return response

    def check_status_by_payjs_order_id(self, payjs_order_id=None):
        """
        通过 PayJS 订单号来查询交易状态
        :param payjs_order_id: PayJS 订单号
        :return: 返回一个 PayJSResult 成员，当其为 SUCCESS 时存在一个 PAID 属性来表明是否已支付
        """
        if not payjs_order_id:
            payjs_order_id = self.payjs_order_id
            if not payjs_order_id:
                raise ValueError('无效的订单号（目前仅支持 PayJS 订单号查询）')

        payjs_order_id = str(payjs_order_id)

        if not 1 <= len(payjs_order_id) <= 32:
            raise ValueError('订单号位数错误（订单号需要在 1 - 32 位）')

        url = r'https://payjs.cn/api/check'

        data = {
            'payjs_order_id': payjs_order_id,
        }

        ret = self.request(url, data)

        # return self.request(url, data)
        return ret

    check_status = check_status_by_payjs_order_id  # 由于目前只支持通过 PayJS 订单号来查询交易状态，因此简写

    # check = check_status_by_payjs_order_id

    def check_url(self, url=None):
        """
        检测回调 URL 是否符合规范
        目前支持普通网址（纯网址必须以/结尾）、带端口的网址、纯 IP 地址、中文网址（需先进行 PunyCode 编码）

        默认只支持 https，要想支持 HTTP 请手动设置实例的 FORCE_SSL 为 False
        :param url: 要检测的网址
        :return: 是否通过（空网址直接通过）
        """
        if not url:
            return True

        r_protocal = r'https' if self.FORCE_SSL else r'http|https'
        r_url = r'(xn--)?[A-Za-z0-9\.]{1,}\.([A-Za-z]{2,6}|xn--[A-Za-z0-9]{1,})'
        r_ip = r'\.'.join([r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)'] * 4)
        r_port = r'\d{1,5}'
        r_path = r'[A-Za-z\.\/]*'

        r = r'^(?P<protocal>{}):\/\/((?P<url>{})|(?P<ip>{}))(:(?P<port>{}))?\/(?P<path>{})$'.format(r_protocal, r_url,
                                                                                                    r_ip, r_port,
                                                                                                    r_path)
        r = re.compile(r)
        if r.match(url):
            return True
        else:
            return False

    def native(self, total_fee: int, out_trade_no, body: str = '', notify_url=None):
        """
        发起扫码支付
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :return:
        """
        url = r'https://payjs.cn/api/native'

        if not total_fee > 0:
            raise ValueError("金额必须为正整数（单位为分）")
        if not total_fee <= 1000000:
            raise ValueError("金额最高为 10000 元")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            raise ValueError("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            raise ValueError("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            raise ValueError("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not self.check_url(notify_url):
            raise ValueError('通知回调地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
        }

        ret = self.request(url, data)
        return ret

    def cashier(self, total_fee: int, out_trade_no, body: str = '', notify_url=None, callback_url=None):
        """
        发起收银台支付

        注：目前此接口在参数传递错误时并不会有提示，依然会返回一个跳转后的网址
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param callback_url: （可选）（暂无效）支付成功后前端跳转地址
        :return: PayJSResult
        """
        url = r'https://payjs.cn/api/cashier'

        if not total_fee > 0:
            raise ValueError("金额必须为正整数（单位为分）")
        if not total_fee <= 1000000:
            raise ValueError("金额最高为 10000 元")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            raise ValueError("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            raise ValueError("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            raise ValueError("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not self.check_url(notify_url):
            raise ValueError('通知回调地址有误')

        if not self.check_url(callback_url):
            raise ValueError('前端跳转地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
            'callback_url': callback_url,
        }

        ret = self.request(url, data)
        return ret

    QRPay = native
    CashierPay = cashier


class PayJSResultBase(PayJS):
    def __init__(self, base: PayJS, raw_response: requests.Response, r_json: dict = None):
        super(PayJSResultBase, self).__init__(mchid=base.mchid, key=base.key)

        self.raw_response = raw_response  # 原始 requests.Response 数据
        self.content = raw_response.content  # 原始 response 的 content
        self.url = raw_response.url  # 请求的 url
        self.STATUS_CODE = raw_response.status_code  # HTTP 请求返回的状态吗
        self.json = r_json  # 请求返回的内容包装后的 JSON 值（以 dict 存储或为 None/False）
        self.JSON = self.json

    def __repr__(self):
        d = self.__dict__
        for m in ('key', 'content', 'raw_response',):
            try:
                d.pop(m)
            except KeyError:
                continue
        return pformat(d)


class PayJSResultSuccess(PayJSResultBase):
    def __init__(self, raw_response: requests.Response, **kwargs):
        super(PayJSResultSuccess, self).__init__(raw_response=raw_response, **kwargs)
        self.RESULT = 'SUCCESS'  # 请求结果（用于输出）
        self.SUCCESS = True  # 请求结果（用于判断）

        if type(self.json) is dict:
            for k, v in self.json.items():
                if k not in ['sign']:
                    setattr(self, k, v)

        if '/api/check' in self.url:
            self.PAID = True if getattr(self, 'status') == 1 else False  # 是否已支付
        if '/api/cashier' in self.url:
            self.REDIRECT = raw_response.headers.get('Location')


class PayJSResultFail(PayJSResultBase):
    ERROR_NO = 0
    ERROR_MSG = ''

    def __init__(self, raw_response: requests.Response, **kwargs):
        super(PayJSResultFail, self).__init__(raw_response=raw_response, **kwargs)
        self.SUCCESS = False  # 请求结果（用于输出）
        self.RESULT = 'FAIL'  # 请求结果（用于判断）
        if not self.json:
            self.ERROR_MSG = '请求失败'  # 错误信息
        else:
            self.ERROR_MSG = self.json.get('msg') or self.json.get('return_msg')


if __name__ == '__main__':
    pass
