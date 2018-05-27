import logging
from payjs.sign import check_signature
from pprint import pformat
from datetime import datetime

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

        self.total_fee = int(notify['total_fee'])

        self.payjs_order_id = notify['payjs_order_id']
        self.out_trade_no = notify['out_trade_no']
        self.transaction_id = notify['transaction_id']

        self.openid = notify['openid']
        self.attach = notify['attach']

        try:
            self.time_end = datetime.strptime(notify['time_end'], '%Y-%m-%d %H:%M:%S')
        except:
            self.time_end = notify['time_end']

        self.mchid = notify['mchid']

    def as_dict(self, params=None):
        if params is None:
            params = (
                'mchid', 'paid', 'total_fee', 'payjs_order_id', 'out_trade_no', 'transaction_id', 'openid', 'attach',
                'time_end'
            )

        d = {}
        for param in params:
            d.setdefault(param, self.__getattribute__(param))

        if 'attach' in d:
            d['attach'] = str(d['attach'])
        if 'time_end' in d:
            if type(self.time_end) is not str:
                d['time_end'] = self.time_end.strftime('%Y-%m-%d %H:%M:%S')

        return d

    def __repr__(self):
        return pformat(self.__dict__)
