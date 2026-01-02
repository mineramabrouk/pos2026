from django.contrib import admin
from .models import Category, Product, Sale, SaleItem, ExchangeRate

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'date_set')
    ordering = ('-date_set',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'price_usd', 'stock', 'last_updated')
    list_filter = ('category', 'last_updated')
    search_fields = ('name', 'barcode')
    readonly_fields = ('price_usd', 'last_updated')

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('total',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'salesperson', 'date_added', 'total_amount')
    inlines = [SaleItemInline]
    readonly_fields = ('receipt_number', 'date_added', 'total_amount')
