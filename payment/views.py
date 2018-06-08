from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from paypal.standard.forms import PayPalPaymentsForm
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# 正在支付中
def payment_process(request):
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



# 支付成功
@csrf_exempt
def payment_done(request):
    return render(request, 'payment/done.html')

# 取消支付
@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html')
