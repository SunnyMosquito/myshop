from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    # db_index，建立数据库索引
    name = models.CharField(verbose_name=_('name'), max_length=200, db_index=True)
    # Slug 是一个新闻术语，是指某个事件的短标签。
    # 它只能由字母，数字，下划线或连字符组成。
    # 通赏情况下，它被用做网址的一部分
    slug = models.SlugField(verbose_name=_('slug'), max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name=_('category'), on_delete=models.CASCADE, related_name='products')
    name = models.CharField(verbose_name=_('name'), max_length=200, db_index=True)
    slug = models.SlugField(verbose_name=_('slug'), max_length=200, db_index=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    # 十进制字段,使用Python的decimal.Decimal元类来保存一个固定精度的十进制数, 
    # max_digits数字允许的最大位数,decimal_places小数的最大位数
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(verbose_name=_('stock'))  # 正整数字段, 库存
    available = models.BooleanField(verbose_name=_('available'), default=True)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)

    class Meta:
        ordering = ('name',)
        # index_together 元选项指定 id 和 slug 字段的共同索引。
        index_together = (('id', 'slug'),)
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    def __str__(self):
        return self.name


