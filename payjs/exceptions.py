class PayJSException(Exception):

    def __init__(self, code, msg):
        """
        :param code: Error code
        :param msg: Error message
        """
        self.code = code
        self.msg = msg

    def __str__(self):
        return '[ERROR] Code: {code}, Message: {msg}'.format(
            code=self.code,
            msg=self.msg
        )

    def __repr__(self):
        return '{klass} Error ({code}:: {msg})'.format(
            klass=self.__class__.__name__,
            code=self.code,
            msg=self.msg
        )


class InvalidSignatureException(PayJSException):

    def __init__(self, code=-1001, msg='Invalid signature'):
        super().__init__(code, msg)


class InvalidInfoException(PayJSException):
    def __init__(self, code=-2000, msg='Invalid info'):
        super().__init__(code, msg)
