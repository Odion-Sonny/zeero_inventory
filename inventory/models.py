from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def current_stock(self):
        in_stock = self.stocktransaction_set.filter(transaction_type='IN').aggregate(total=models.Sum('quantity'))['total'] or 0
        out_stock = self.stocktransaction_set.filter(transaction_type='OUT').aggregate(total=models.Sum('quantity'))['total'] or 0
        return in_stock - out_stock

    def __str__(self):
        return f"{self.name} ({self.sku})"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Restock'),
        ('OUT', 'Sale/Usage'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} - {self.quantity}"
