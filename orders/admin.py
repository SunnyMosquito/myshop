from django.contrib import admin
from .models import Order, OrderItem
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Register your models here.


def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(
        reverse('orders:admin_order_pdf', args=[obj.id])))


# order_pdf.allow_tags = True
order_pdf.short_description = _('PDF bill')

def order_detail(obj):
    return mark_safe('<a href="{}">View</a>'.format(
        reverse('orders:admin_order_detail', args=[obj.id])))

# order_detail.allow_tags = True
order_detail.short_description = _('order detail')


# 导出为csv文件
def export_to_csv(modeladmin, request, queryset):

    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; \
           filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields(
    ) if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = _('Export to CSV')

class OrderItemInline(admin.TabularInline):
    # 在 OrderItem 使用 ModelInline 来把它引用为 OrderAdmin 类的内联元素。
    # 一个内联元素允许你在同一编辑页引用模型，并且将这个模型作为父模型。
    model = OrderItem
    # 生成一个链接，可以点击查看外键的详细信息
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv] # 在列表页面选中项目后要执行的操作，比如删除


admin.site.register(Order, OrderAdmin)
