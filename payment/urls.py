from django.urls import path, include
from . import views

app_name = 'payment'
urlpatterns = [
    path('paypal/process/', views.payment_paypal_process, name='paypal_process'),
    path('alipay/process/', views.payment_alipay_process, name='alipay_process'),
    path('alipay/done/', views.payment_alipay_done, name='alipay_done'),
    path('done/', views.payment_done, name='done'),
    path('canceled/', views.payment_canceled, name='canceled'),
]
