from rest_framework import serializers
from .models import Product, StockTransaction

class ProductSerializer(serializers.ModelSerializer):
    current_stock = serializers.IntegerField(source='current_stock', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'description', 'current_stock', 'created_at', 'updated_at']

class StockTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransaction
        fields = ['id', 'product', 'transaction_type', 'quantity', 'timestamp']
