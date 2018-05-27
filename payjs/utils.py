import re


def check_url(url=None, force_ssl=True):
    """
    检测回调 URL 是否符合规范
    目前支持普通网址（纯网址必须以/结尾）、带端口的网址、纯 IP 地址、中文网址（需先进行 PunyCode 编码）

    默认只支持 https，要想支持 HTTP 请手动设置实例的 FORCE_SSL 为 False
    :param url: 要检测的网址
    :param force_ssl: 是否强制使用 https
    :return: 是否通过（空网址直接通过）
    """
    if not url:
        return True

    r_protocal = r'https' if force_ssl else r'http|https'
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
