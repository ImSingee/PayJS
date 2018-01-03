import os
from PayJS import PayJS

MCHID = os.environ.get('MCHID')
KEY = os.environ.get('KEY')

# 初始化
p = PayJS(MCHID, KEY)

# 扫码支付
OUT_TRADE_NO = '2017TEST'     # 外部订单号（自己的支付系统的订单号，请保证唯一）
TOTAL_FEE = 1                 # 支付金额，单位为分，金额最低 0.01 元最多 10000 元
BODY = '测试支付'              # 订单标题
r = p.QRPay(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, body=BODY)
if r.SUCCESS:
    print(r.code_url)         # 二维码地址（weixin:// 开头，请使用此地址构建二维码）
    print(r.qrcode)           # 二维码地址（https:// 开头，为二维码图片的地址）
    print(r.payjs_order_id)   # 订单号（PAYJS 的）
else:
    print(r.STATUS_CODE)      # HTTP 请求状态码
    print(r.ERROR_NO)         # 错误码
    print(r.ERROR_MSG)        # 错误信息
    print(r)

# 收银台支付
c = p.CashierPay(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, body=BODY)
if c.SUCCESS:
    print(c.REDIRECT)         # 要跳转到的收银台网址
else:
    print(c.ERROR_MSG)        # 错误信息
    print(c)

# 订单查询
s = p.check_status(r.payjs_order_id)
# 或 s = r.check_status()
if s.SUCCESS:
    print(s.PAID)            # 是否已支付
else:
    print(s.ERROR_MSG)       # 错误信息
    print(s)