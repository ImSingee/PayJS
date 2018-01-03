# PayJS
A Python Package for PayJS

## 说明

本项目为 PayJS 的开源 Python SDK，仅支持 Python 3.6 及以上版本，不支持也不打算支持 Python 2，如果您发现此项目在 Python 3.4 及以上版本无法测试通过，请给我提 Issue 或 Pull Request

使用前，您需要在 [PayJS](https://payjs.cn/) 注册一个账号并开通商户。

当前实现了扫码支付与订单查询


## 安装

```bash
$ pipenv install PayJS
```

## 快速开始

```python
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
```

## TODO:

+ 校验回调