# PayJS
A Python Package for PAYJS

## 说明

本项目为 PAYJS 的开源 Python SDK，**仅支持 Python 3.6 及以上版本**。
目前此项目在 Python 3.6 及以上版本测试通过，如果您发现有任何问题，欢迎给我提 Issue 或 Pull Request。

使用前，您需要在 [PAYJS](https://payjs.cn/ref/WDQGQD) 注册一个账号并开通商户。

当前实现了扫码支付、收银台支付与订单查询

## 安装

```bash
$ pip install payjs
```

## 快速开始

```python
from payjs import PayJS # 也可根据个人习惯选择使用 Payjs/PAYJS/payjs
from payjs import PayJSNotify # 也可根据个人习惯选择使用 PayjsNotify/PAYJSNotify

MCHID = '这里是商户号'
KEY = '这里是商户密钥'

# 初始化
p = PayJS(MCHID, KEY)

# 扫码支付
OUT_TRADE_NO = '2017TEST' # 外部订单号（自己的支付系统的订单号，请保证唯一）
TOTAL_FEE = 1 # 支付金额，单位为分，金额最低 0.01 元最多 10000 元
BODY = '测试支付' # 订单标题
NOTIFY_URL = 'https://pay.singee.site/empty/' # Notify 网址
ATTACH = 'info' # Notify 内容
r = p.QRPay(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, body=BODY, notify_url=NOTIFY_URL, attach=ATTACH)
if r:
    print(r.code_url)         # 二维码地址（weixin:// 开头，请使用此地址构建二维码）
    print(r.qrcode)           # 二维码地址（https:// 开头，为二维码图片的地址）
    print(r.payjs_order_id)   # 订单号（PAYJS 的）
else:
    print(r.STATUS_CODE)      # HTTP 请求状态码
    print(r.ERROR_NO)         # 错误码
    print(r.error_msg)        # 错误信息
    print(r)

# 构造收银台支付网址（仅构造链接，请使用浏览器 302 到这个网址，无法预检查调用是否成功）
c = p.get_cashier_url(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, body=BODY, callback_url=CALLBACK_URL, notify_url=NOTIFY_URL, attach=ATTACH)
print(c)

# JSApi 支付
OPENID = '这里填写支付用户的 OpenID' # 支付用户在 PayJS 端的 OpenID，可通过 get_openid 获取
j = p.JSApiPay(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, openid=OPENID, body=BODY, notify_url=NOTIFY_URL, attach=ATTACH)
if j:
    print(j.jsapi)   # 用于发起支付的支付参数
else:
    print(j.STATUS_CODE)      # HTTP 请求状态码
    print(j.ERROR_NO)         # 错误码
    print(j.error_msg)        # 错误信息
    print(j)

# 刷卡支付
AUTH_CODE = '这里填写用户侧 18 位数字' # 用户的支付条码或二维码所对应的数字
m = p.MicroPay(out_trade_no=OUT_TRADE_NO, total_fee=TOTAL_FEE, auth_code=AUTH_CODE, body=BODY)
print(m)

# 订单查询
s = p.check_status(payjs_order_id=r.payjs_order_id)
if s:
    print(s.paid)            # 是否已支付
else:
    print(s.error_msg)       # 错误信息
    print(s)

# 订单关闭
t = p.close(r.payjs_order_id)
if t:
    print('Success')
else:
    print('Error')
    print(t.return_msg)

# 订单退款
t = p.refund(r.payjs_order_id)
if t:
    print('Success')
else:
    print('Error')
    print(t.return_msg)

# 获取用户 OpenId
o = p.get_openid(callback_url=CALLBACK_URL)
print(o)

# 回调验证
n = PayJSNotify(KEY, '回调内容（str 或 dict）')
print(n)
```

## 更多

我在代码中写了相当详细的注释，如果您想要使用超出上面「快速开始」部分的功能，请阅读代码。

如果您希望帮助我完善文档，也欢迎联系我。

## 修正历史

+ v0.9   : A 初稿完成
+ v0.9.2 : A 按照文档添加了收银台支付失败；M 修正了请求错误机制；M 在返回错误的情况下忽略签名
+ v0.9.3 : M 简化是否成功判断; M 在返回错误的情况下不再忽略签名 
+ v0.9.4 : A 添加了关闭订单; M 修正 PyPi GBK 编码问题
+ v0.9.5 : A 添加了 attach 支持
+ v1.0.0 : **不向下支持** 全新发布
+ v1.1.0 : A 添加了 notify 解析支持
+ v1.1.5 : M 添加了 cashier_legacy 兼容模式
+ v1.1.6 : A 添加了退款接口支持
+ v1.2.0 : A 添加了刷卡支付接口支持
+ v1.2.1 : A 添加了构造 OpenId 网址支持
+ v1.2.2 : A 添加了 JSAPI 支付接口支持
+ v1.2.4 : M 修复了网址判断正则表达式 Path 的部分 bug
+ v1.2.5 : A 添加了收银台接口对 auto 与 hide 字段的支持

## 联系我

+ Email：imsingee@gmail.com
+ 其他：本 repo 的 Issue

## v0.9 升级至 v1.0

1. 将 `from PayJs import ...` 改为 `from payjs import ...`
2. 不要使用 result 进行任何操作（例如查询、关闭订单等）
3. 使用 `check_status` 时手动指定参数 `payjs_order_id=`
4. result 的 SUCCESS、ERROR、RESULT 不再可用，请使用 bool() 进行判断状态
5. 签名错误直接抛出异常
6. import 时不应再导入任何 Result 类
7. result 的 `ERROR_MSG` 不再可用，请替换为 `error_msg`