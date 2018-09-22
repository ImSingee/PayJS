import json
import logging
import requests

from pprint import pformat
from urllib.parse import urlencode

from payjs.result import PayJSResultSuccess, PayJSResultFail
from payjs.sign import get_signature, check_signature
from payjs.utils import check_url
from payjs.exceptions import InvalidSignatureException, InvalidInfoException

logger = logging.getLogger(__name__)


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
            raise InvalidInfoException(-2001, "商户号格式必须为字符串")

        self.mchid = mchid

        if type(key) is not str:
            raise InvalidInfoException(-2002, "密钥格式必须为字符串")

        self.key = key

        if not check_url(notify_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2003, "通知回调网址错误")

        self.notify_url = notify_url

    def request(self, url: str, data: dict, method='POST'):
        """
        处理请求（请求时会过滤值为空的参数）

        :param url: 请求的 url
        :param data: 请求的参数字典（不包含签名）
        :return: 返回一个 PayJSResultSuccess 或 PayJSResultFail 类元素
        """
        data['sign'] = get_signature(self.key, data)
        data = {k: v for k, v in data.items() if v}
        if method == 'GET':
            r = requests.get(url, params=data, allow_redirects=False)
        else:
            r = requests.post(url, data=data, allow_redirects=False)

        return self.parse_response(r)

    def parse_response(self, raw_response: requests.Response):
        """
        处理请求，将 requests 的返回包装为 PayJSResult
        :param raw_response: requests 的返回值
        :return: 一个 PayJSResult 元素（Success 或 Fail）
        """
        if raw_response.status_code == 200:
            # 扫码支付 与 订单查询；收银台支付失败
            try:
                j = json.loads(raw_response.content)
            except json.JSONDecodeError:
                return PayJSResultFail(raw_response=raw_response, r_json=False)
            except UnicodeDecodeError:
                return PayJSResultFail(raw_response=raw_response, r_json=False)

            try:
                check_signature(self.key, j)
            except InvalidSignatureException:
                response = PayJSResultFail(raw_response=raw_response, r_json=j)
                response.error_msg = '返回的签名错误'

            if str(j.get('return_code')) == '0':  # 请求失败
                response = PayJSResultFail(raw_response=raw_response, r_json=j)
            else:
                response = PayJSResultSuccess(raw_response=raw_response, r_json=j)

        elif raw_response.status_code == 302:
            # 收银台支付
            return PayJSResultSuccess(raw_response=raw_response, r_json=None)
        else:
            response = PayJSResultFail(raw_response=raw_response, r_json=False)
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
                raise InvalidInfoException(-3001, '无效的订单号（目前仅支持 PayJS 订单号查询）')

        payjs_order_id = str(payjs_order_id)

        if not 1 <= len(payjs_order_id) <= 32:
            logger.warning('订单号位数可能错误（需要在 1 - 32 位）')

        url = r'https://payjs.cn/api/check'

        data = {
            'payjs_order_id': payjs_order_id,
        }

        ret = self.request(url, data)

        # return self.request(url, data)
        return ret

    def check_status(self, *, payjs_order_id=None):
        return self.check_status_by_payjs_order_id(payjs_order_id)

    def native(self, total_fee: int, out_trade_no, body: str = '', notify_url=None, attach=None):
        """
        发起扫码支付
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :return:
        """
        url = r'https://payjs.cn/api/native'

        if not total_fee > 0:
            raise InvalidInfoException(-2004, "金额必须为正整数（单位为分）")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            logger.warning("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            logger.warning("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            logger.warning("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not check_url(notify_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2003, '通知回调地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
            'attach': attach,
        }

        ret = self.request(url, data)
        return ret

    def cashier(self, total_fee: int, out_trade_no, body: str = '', notify_url=None, callback_url=None, attach=None):
        """
        发起收银台支付【未来应该会使用这个接口，现在暂时还不能用】

        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param callback_url: （可选）支付成功后前端跳转地址
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :return: PayJSResult
        """
        logger.warning('此接口目前情况下使用会出问题，请使用 cashier_legacy 直接获取构造出的跳转网址')
        url = r'https://payjs.cn/api/cashier'

        if not total_fee > 0:
            raise InvalidInfoException(-2004, "金额必须为正整数（单位为分）")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            logger.warning("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            logger.warning("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            logger.warning("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not check_url(notify_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2003, '通知回调地址有误')

        if not check_url(callback_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2004, '前端跳转地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
            'callback_url': callback_url,
            'attach': attach
        }

        ret = self.request(url, data, method='gulp')
        return ret

    def cashier_legacy(self, total_fee: int, out_trade_no, body: str = '', notify_url=None, callback_url=None,
                       attach=None):
        """
        发起收银台支付【Legacy 临时可用】

        【此接口无法判断是否请求成功会直接返回 URL 构造地址】

        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param callback_url: （可选）支付成功后前端跳转地址
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :return: PayJSResult
        """
        url = r'https://payjs.cn/api/cashier'

        if not total_fee > 0:
            raise InvalidInfoException(-2004, "金额必须为正整数（单位为分）")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            logger.warning("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            logger.warning("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            logger.warning("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not check_url(notify_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2003, '通知回调地址有误')

        if not check_url(callback_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2004, '前端跳转地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
            'callback_url': callback_url,
            'attach': attach
        }

        data['sign'] = get_signature(self.key, data)
        data = {k: v for k, v in data.items() if v}

        return url + '?' + urlencode(data)

    def jsapi(self, total_fee: int, out_trade_no, openid, body: str = '', notify_url=None, attach=None):
        """
        发起 JSAPI 支付
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param openid: 用户 OpenID，可通过调用 get_openid 获得
        :param body: （可选）订单标题，0 - 32 字符
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :return:
        """
        url = r'https://payjs.cn/api/jsapi'

        if not total_fee > 0:
            raise InvalidInfoException(-2004, "金额必须为正整数（单位为分）")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            logger.warning("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            logger.warning("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            logger.warning("标题最多为 32 位")

        if notify_url is None:
            notify_url = self.notify_url
        if not check_url(notify_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2003, '通知回调地址有误')

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'notify_url': notify_url,
            'attach': attach,
            'openid': openid,
        }

        ret = self.request(url, data)
        return ret

    def micropay(self, total_fee: int, out_trade_no, auth_code, body: str = ''):
        """
        发起刷卡支付
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param out_trade_no: 订单号，应保证唯一性，1-32 字符
        :param auth_code: 刷卡支付授权码，设备读取用户微信中的条码或者二维码信息，18 位纯数字，以 10、11、12、13、14、15 开头
        :param body: （可选）订单标题，0 - 32 字符
        :return:
        """
        url = r'https://payjs.cn/api/micropay'

        if not total_fee > 0:
            raise InvalidInfoException(-2004, "金额必须为正整数（单位为分）")

        out_trade_no = str(out_trade_no)

        if not out_trade_no:
            logger.warning("用户端订单号不可省略")
        if not len(out_trade_no) <= 32:
            logger.warning("用户端订单号最多为 32 位")

        if not len(body) <= 32:
            logger.warning("标题最多为 32 位")

        if not str(auth_code).isdigit() or not len(str(auth_code)) == 18:
            logger.warning("刷卡支付授权码应为 18 位纯数字")

        data = {
            'mchid': self.mchid,
            'total_fee': total_fee,
            'out_trade_no': out_trade_no,
            'body': body,
            'auth_code': auth_code,
        }

        ret = self.request(url, data)
        return ret

    def close(self, payjs_order_id=None):
        """
        通过 PayJS 订单号来查询交易状态
        :param payjs_order_id: PayJS 订单号
        :return: 返回一个 PayJSResult 成员，当其为 SUCCESS 时存在一个 PAID 属性来表明是否已支付
        """
        if not payjs_order_id:
            payjs_order_id = self.payjs_order_id
            if not payjs_order_id:
                raise InvalidInfoException(-2005, '未提供订单号')

        payjs_order_id = str(payjs_order_id)

        if not 1 <= len(payjs_order_id) <= 32:
            logger.warning('订单号可能错误（位数需要在 1 - 32 位）')

        url = r'https://payjs.cn/api/close'

        data = {
            'payjs_order_id': payjs_order_id,
        }

        ret = self.request(url, data)

        # return self.request(url, data)
        return ret

    def refund(self, payjs_order_id=None):
        """
        通过 PayJS 订单号退款
        :param payjs_order_id: PayJS 订单号
        :return: 返回一个 PayJSResult 成员，当其为 SUCCESS 时存在一个 PAID 属性来表明是否已支付
        """
        if not payjs_order_id:
            payjs_order_id = self.payjs_order_id
            if not payjs_order_id:
                raise InvalidInfoException(-2005, '未提供订单号')

        payjs_order_id = str(payjs_order_id)

        if not 1 <= len(payjs_order_id) <= 32:
            logger.warning('订单号可能错误（位数需要在 1 - 32 位）')

        url = r'https://payjs.cn/api/refund'

        data = {
            'payjs_order_id': payjs_order_id,
        }

        ret = self.request(url, data)

        return ret

    def get_openid(self, callback_url):
        """
        获取 OpenID

        会返回一个构造的 url，直接通过浏览器跳转该 url 即可；在微信环境下，微信浏览器会自动跳转至 callback_url，并携带名称为 openid 的查询参数

        :param callback_url: 支付成功后前端跳转地址
        :return: PayJSResult
        """
        url = r'https://payjs.cn/api/openid'

        if not check_url(callback_url, force_ssl=self.FORCE_SSL):
            raise InvalidInfoException(-2004, '前端跳转地址有误')

        data = {
            'callback_url': callback_url,
        }

        # data = {k: v for k, v in data.items() if v}

        return url + '?' + urlencode(data)

    QRPay = native
    CashierPay = cashier
    JSPay = jsapi
    JSApiPay = jsapi
    MicroPay = micropay
