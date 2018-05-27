import logging
from hashlib import md5
from urllib.parse import urlencode, unquote_plus

from payjs.exceptions import InvalidSignatureException

logger = logging.getLogger(__name__)


def get_signature(key: str, data: dict):
    """
    签名过程如下：
    0. 忽略已经存在的 sign
    1. 将所有参数名按照字典序排列，并以 "参数1=值1&参数2=值2&参数3=值3" 的形式排序
    2. 将上面的内容加上 "&key=KEY"（KEY 为设置的商户密钥）
    3. 将组合后的字符串转换为大写 MD5

    :param key: 商户密钥
    :param data: 要签名的参数字典
    :return: 签名后的字符串
    :rtype: str
    """
    d = data.copy()

    # pop 掉 sign 字段
    try:
        d.pop('sign')
    except KeyError:
        pass

    # pop 掉无效字段
    p = sorted([x for x in d.items() if (x[1] or x[1] == 0)], key=lambda x: x[0])

    p.append(('key', key))

    p = unquote_plus(urlencode(p))

    h = md5()
    h.update(p.encode())

    r = h.hexdigest().upper()

    return r


def check_signature(key: str, data: dict, sign: str = None):
    """
       校验签名，签名不通过会抛出 InvalidSignature 异常
       :param key: 商户密钥
       :param data: 要签名的参数字典
       :param sign: 要校验的签名，省略（为 None）则从 data 中取 sign 字段
       :rtype: bool
       """
    if sign is None:
        sign = data.get('sign')

    if get_signature(key, data) == sign:
        return True

    raise InvalidSignatureException
