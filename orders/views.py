from django.shortcuts import render, redirect
from django.urls import reverse
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .task import order_created
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Order
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

# Create your views here.

# 管理页面下载发票
@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=\
           "order_{}.pdf"'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[weasyprint.CSS(
                                               settings.STATIC_ROOT + 'css/pdf.css')])
    return response

# 订单详细页面
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})

# 创建订单
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 如果表单验证成功，将模型表单保存到数据库
            order = form.save(commit=False)
            # 有优惠卷就增加到订单表中
            if cart.coupon:
            	order.coupon = cart.coupon
            	order.discount = cart.coupon.discount
            order.save()
            # 将购物车物品添加到orderitem中
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()

            # items = []
            # for item in order.items.all():
            #     items.append(item.product)
            # print(items)

            # launch asynchronous task，order_created是task里的函数
            order_created.delay(order.id)  # set the order in the session
            request.session['order_id'] = order.id  # redirect to the payment
            # return redirect(reverse('payment:process'))
            return render(request,
                          'orders/order/payment.html')

    # get请求创建订单
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})
