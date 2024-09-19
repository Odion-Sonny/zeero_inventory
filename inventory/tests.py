from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from decimal import Decimal
from .models import Product, StockTransaction
from .forms import ProductForm

class ProductModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST123',
            price=Decimal('10.99'),
            description='A test product description.'
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.sku, 'TEST123')
        self.assertEqual(self.product.price, Decimal('10.99'))
        self.assertEqual(self.product.description, 'A test product description.')

    def test_sku_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name='Another Product',
                sku='TEST123', 
                price=Decimal('15.99'),
                description='Another description.'
            )

class ProductFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'name': 'New Product',
            'sku': 'NEW123',
            'price': Decimal('20.99'),
            'description': 'A new product description.'
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'name': 'Invalid Product',
            'sku': '', 
            'price': Decimal('20.99'),
            'description': 'A new product description.'
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)

class ProductViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST123',
            price=Decimal('10.99'),
            description='A test product description.'
        )

    def test_create_product_view(self):
        response = self.client.post(reverse('inventory:create_product'), {
            'name': 'Another Product',
            'sku': 'ANOTHER123',
            'price': Decimal('25.99'),
            'description': 'Another product description.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(sku='ANOTHER123').exists())

    def test_edit_product_view(self):
        response = self.client.post(reverse('inventory:edit_product', args=[self.product.pk]), {
            'name': 'Updated Product',
            'sku': 'TEST123',
            'price': Decimal('30.99'),
            'description': 'Updated description.'
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, Decimal('30.99'))
        self.assertEqual(self.product.description, 'Updated description.')
        self.assertEqual(response.status_code, 302) 

    def test_delete_product_view(self):
        response = self.client.post(reverse('inventory:delete_product', args=[self.product.pk]))
        self.assertEqual(response.status_code, 302) 
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

class StockTransactionModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST123',
            price=Decimal('10.99'),
            description='A test product description.'
        )
        self.transaction = StockTransaction.objects.create(
            product=self.product,
            transaction_type='IN',
            quantity=30
        )

    def test_stock_transaction_creation(self):
        self.assertEqual(self.transaction.product, self.product)
        self.assertEqual(self.transaction.transaction_type, 'IN')
        self.assertEqual(self.transaction.quantity, 30)

    def test_stock_transaction_str(self):
        self.assertEqual(str(self.transaction), 'Restock - Test Product - 30')

class ReportViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST123',
            price=Decimal('10.99'),
            description='A test product description.'
        )
        StockTransaction.objects.create(
            product=self.product,
            transaction_type='IN',
            quantity=50
        )
        StockTransaction.objects.create(
            product=self.product,
            transaction_type='OUT',
            quantity=20
        )

    def test_generate_csv_report(self):
        response = self.client.get(reverse('inventory:generate_csv_report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response.content.startswith(b'Name,SKU,Price,Current Stock'))
        self.assertIn(b'Test Product,TEST123,10.99,30', response.content)
