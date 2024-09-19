from django.contrib import admin
from .models import Product, StockTransaction

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'current_stock', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('created_at',)

    def current_stock(self, obj):
        return obj.current_stock()
    current_stock.short_description = 'Current Stock'

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('product__name', 'product__sku')
