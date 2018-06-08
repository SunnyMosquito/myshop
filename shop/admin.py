from django.contrib import admin
from .models import Category, Product

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    # prepopulated_fields 属性来指定那些要使用其他字段来自动赋值的字段
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    # 在列表页面可以编辑
    list_editable = ['price', 'stock', 'available'] 
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Product, ProductAdmin)
