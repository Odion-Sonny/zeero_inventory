from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, StockTransaction
from .forms import ProductForm, StockTransactionForm
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.db import models

from django.http import HttpResponse
import csv
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/create_product.html', {'form': form})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/edit_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory:product_list')
    return render(request, 'inventory/delete_product_confirm.html', {'product': product})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def add_stock_transaction(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('inventory:product_list')
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/add_stock_transaction.html', {'form': form})

# def inventory_report(request):
#     products = Product.objects.annotate(
#         total_in=Sum('stocktransaction__quantity', filter=models.Q(stocktransaction__transaction_type='IN')),
#         total_out=Sum('stocktransaction__quantity', filter=models.Q(stocktransaction__transaction_type='OUT'))
#     )

#     recent_transactions = StockTransaction.objects.order_by('-timestamp')[:10]

#     report = []
#     for product in products:
#         current_stock = (product.total_in or 0) - (product.total_out or 0)
#         report.append({
#             'name': product.name,
#             'sku': product.sku,
#             'price': product.price,
#             'current_stock': current_stock,
#         })
#     # return render(request, 'inventory/inventory_report.html', {'report': report})
#     return render(request, 'inventory/inventory_report.html', {'report': report, 'recent_transactions': recent_transactions,})


# def generate_csv_report(request):
#     import csv
#     from django.http import HttpResponse

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Name', 'SKU', 'Price', 'Current Stock'])

#     products = Product.objects.all()
#     for product in products:
#         writer.writerow([
#             product.name,
#             product.sku,
#             product.price,
#             product.current_stock(),
#         ])

#     return response






def inventory_report(request):
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()

    if filter_type == 'daily':
        start_date = today
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif filter_type == 'monthly':
        start_date = today - timedelta(days=30)
    else:
        start_date = None

    products = Product.objects.annotate(
        total_in=Sum('stocktransaction__quantity', filter=Q(stocktransaction__transaction_type='IN')),
        total_out=Sum('stocktransaction__quantity', filter=Q(stocktransaction__transaction_type='OUT'))
    )

    if start_date:
        recent_transactions = StockTransaction.objects.filter(timestamp__gte=start_date).order_by('-timestamp')
    else:
        recent_transactions = StockTransaction.objects.order_by('-timestamp')[:10]

    report = []
    for product in products:
        current_stock = (product.total_in or 0) - (product.total_out or 0)
        report.append({
            'name': product.name,
            'sku': product.sku,
            'price': product.price,
            'current_stock': current_stock,
        })
    
    return render(request, 'inventory/inventory_report.html', {
        'report': report,
        'recent_transactions': recent_transactions,
        'filter_type': filter_type,
    })

def generate_csv_report(request):
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()

    if filter_type == 'daily':
        start_date = today
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif filter_type == 'monthly':
        start_date = today - timedelta(days=30)
    else:
        start_date = None

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'SKU', 'Price', 'Current Stock'])

    products = Product.objects.annotate(
        total_in=Sum('stocktransaction__quantity', filter=Q(stocktransaction__transaction_type='IN')),
        total_out=Sum('stocktransaction__quantity', filter=Q(stocktransaction__transaction_type='OUT'))
    )

    if start_date:
        recent_transactions = StockTransaction.objects.filter(timestamp__gte=start_date)
    else:
        recent_transactions = StockTransaction.objects.all()

    for product in products:
        current_stock = (product.total_in or 0) - (product.total_out or 0)
        writer.writerow([
            product.name,
            product.sku,
            product.price,
            current_stock,
        ])

    return response