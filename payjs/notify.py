import logging
from payjs.sign import check_signature
from pprint import pformat

logger = logging.getLogger(__name__)


class PayJSNotify:
    def __init__(self, key: str, notify_content, mchid=None):
        if type(notify_content) is str:
            from urllib import parse
            notify = dict(parse.parse_qsl(notify_content))
        else:
            notify = dict(notify_content)

        logger.debug('notify: {}'.format(notify))

        check_signature(key, notify)

        self.mchid = notify['mchid']

        if mchid is not None and self.mchid != mchid:
            logger.warning('商户号不符')

        self.return_code = notify['return_code']

        if int(self.return_code) == 1:
            self.paid = True
        else:
            self.paid = False

        self.total_fee = notify['total_fee']

        self.payjs_order_id = notify['payjs_order_id']
        self.out_trade_no = notify['out_trade_no']
        self.transaction_id = notify['transaction_id']

        self.openid = notify['openid']
        self.attach = notify['attach']
        self.time_end = notify['time_end']

        self.mchid = notify['mchid']

    def __str__(self):
        return pformat(self.__dict__)

    def __repr__(self):
        return '<PayJSNotify> ({})'.format(', '.join(self.__dict__.keys()))
