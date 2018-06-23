from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from paypal.standard.forms import PayPalPaymentsForm
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt
from alipay import AliPay
from django.http.response import HttpResponse

# Create your views here.

# 正在支付中
def payment_paypal_process(request):
    order_id = request.session.get('order_id') # 获得订单id
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host() # 获得host，即网址
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL, # 商户帐号，收款账户
        'amount': '%.2f' % order.get_total_cost().quantize(
            Decimal('.01')), # 金额
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id), # 发票号
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')), # 通知url，即ajax的post请求返回的url
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment:done')), # 成功后返回商家的url
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment:canceled')), # 支付取消的url
    }
    form = PayPalPaymentsForm(initial=paypal_dict) # 实例化paypay支付表单，点击该表单跳转到paypal支付页面
    return render(request,
                  'payment/process.html',
                  {'order': order, 'form': form})

def payment_alipay_process(request):
    order_id = request.session.get('order_id') # 获得订单id
    order = get_object_or_404(Order, id=order_id)

    app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
    host = request.get_host() # 获得host，即网址

    alipay = AliPay(
        appid="2016091400505954",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2", # RSA 或者 RSA2
        debug=settings.DEBUG  # 默认False
    )

    subject = "测试订单"

    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no = order.id,
        total_amount = '{0:.2}'.format(order.get_total_cost().quantize(Decimal('.01'))),
        subject = subject,
        return_url= 'http://{}{}'.format(host,
                                         reverse('payment:alipay_done')), # 成功后返回商家的url
        notify_url= 'https://{}{}'.format(host,
                                         reverse('payment:alipay_done')) # 可选, 不填则使用默认notify url
    )

    # import pdb
    # pdb.set_trace()
    if settings.DEBUG:
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
    else:
        pay_url = 'https://openapi.alipay.com/gateway.do?' + order_string
    return redirect(pay_url)

@csrf_exempt
def payment_alipay_done(request):
    app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

    alipay = AliPay(
        appid="2016091400505954",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2", # RSA 或者 RSA2
        debug=settings.DEBUG  # 默认False
    )
 
    if request.method == 'POST':
        data = dict()
        for key, value in request.POST.items():
            data[key] = value
        signature = data.pop('sign')
        success = alipay.verify(data, signature)
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
            order_id = data.get('out_trade_no') # 获得订单id
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.save()
            print("trade succeed")
            return HttpResponse('success')
        else:
            print("交易失败")
            return HttpResponse('error')
    else:
        order_id = request.GET.get('out_trade_no') # 获得订单id
        order = Order.objects.get(id=order_id)
        if order.paid:
            return redirect(reverse('payment:done'))
        else:
            return render(request, 'payment/alipay/process.html')

# 支付成功
@csrf_exempt
def payment_done(request):
    return render(request, 'payment/done.html')

# 取消支付
@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html')
