from . import views
from django.urls import path, include
'''
path不支持正则。要用正则需要导入re_path
'''
app_name = 'shop'
urlpatterns = [
    path('', views.product_list, name='product_list'), # 产品列表页，也是主页
    path('<str:category_slug>/', \
         views.product_list, name='product_list_by_category'), # 分类的产品列表页
    path('<int:id>/<str:slug>/',
         views.product_detail, name='product_detail'), # 产品详细页面
]
