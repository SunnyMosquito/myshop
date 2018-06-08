"""myshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myshop import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# 国际化模式，url前面带en,zh等
urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')), # 购物车
    path('orders/',include('orders.urls')), # 订单页
    path('paypal/', include('paypal.standard.ipn.urls')), # paypal
    path('payment/', include('payment.urls')), # 支付网关
    path('coupons/', include('coupons.urls')), # 优惠卷
    path('rosetta/', include('rosetta.urls')), # 可视化翻译页面
    path('', include('shop.urls')),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
