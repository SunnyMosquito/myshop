from django.db import models
from shop.models import Product
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupons.models import Coupon
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Order(models.Model):
    coupon = models.ForeignKey(Coupon,
                               verbose_name=_('coupon'),
                               related_name='orders',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)


    discount = models.IntegerField(default=0,
                                   verbose_name=_('discount'),
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    first_name = models.CharField(verbose_name=_('first_name'),max_length=50)
    last_name = models.CharField(verbose_name=_('last_name'),max_length=50)
    email = models.EmailField(verbose_name=_('email'))
    address = models.CharField(verbose_name=_('address'),max_length=250)
    postal_code = models.CharField(verbose_name=_('postal-code'),max_length=20) # 邮编
    city = models.CharField(verbose_name=_('city'),max_length=100)
    created = models.DateTimeField(verbose_name=_('created'),auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'),auto_now=True)
    paid = models.BooleanField(verbose_name=_('paid'),default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)
    
    def get_total_cost(self):
        # 这里的items是关系名，跟orderitem的一对多关系，获取所有item
        # 求出订单总金额
	    total_cost = sum(item.get_cost() for item in self.items.all())
	    return total_cost - total_cost * (self.discount / Decimal('100'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_('order'), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name=_('product'), on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, verbose_name=_('price'), decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'),default=1)

    def __str__(self):
        return '{}'.format(self.id)
    
    # 返回一件商品的总价
    def get_cost(self):
        return self.price * self.quantity
