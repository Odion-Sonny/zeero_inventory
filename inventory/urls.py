from django.urls import path, include
from rest_framework import routers
from django.contrib import admin
from . import views, api_views

app_name = 'inventory'
router = routers.DefaultRouter()
router.register(r'api/products', api_views.ProductViewSet)
router.register(r'api/transactions', api_views.StockTransactionViewSet)

urlpatterns = [
    path('products/create/', views.create_product, name='create_product'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('transactions/add/', views.add_stock_transaction, name='add_stock_transaction'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/inventory/csv/', views.generate_csv_report, name='generate_csv_report'),
    path('', include(router.urls)),

]
