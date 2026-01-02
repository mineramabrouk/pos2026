import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_project.settings')
django.setup()

from sales.models import Product, Category, ExchangeRate

def test_price_calculation():
    print("Testing Price Calculation...")
    
    # Clean up
    Product.objects.all().delete()
    ExchangeRate.objects.all().delete()
    Category.objects.all().delete()

    # Create Category
    cat = Category.objects.create(name="Electronics")

    # 1. Test without Exchange Rate
    p1 = Product.objects.create(
        name="Mouse",
        category=cat,
        price=Decimal('70.00'),
        cost=Decimal('50.00'),
        stock=10
    )
    print(f"Product created without rate. Price USD: {p1.price_usd} (Expected: None)")

    # 2. Create Exchange Rate
    rate = ExchangeRate.objects.create(rate=Decimal('6.96'))
    print(f"Created Exchange Rate: {rate.rate}")

    # 3. Update Product (should trigger calculation)
    p1.save()
    print(f"Product saved. Price: {p1.price}, Rate: {rate.rate}")
    print(f"Price USD: {p1.price_usd} (Expected: {70/6.96:.2f})")

    # 4. Create new Product with Rate existing
    p2 = Product.objects.create(
        name="Keyboard",
        category=cat,
        price=Decimal('100.00'),
        cost=Decimal('80.00'),
        stock=5
    )
    print(f"New Product created. Price: {p2.price}")
    print(f"Price USD: {p2.price_usd} (Expected: {100/6.96:.2f})")

    # 5. Update Exchange Rate and Product
    new_rate = ExchangeRate.objects.create(rate=Decimal('7.00'))
    print(f"New Exchange Rate: {new_rate.rate}")
    
    p2.save()
    print(f"Product 2 updated. Price USD: {p2.price_usd} (Expected: {100/7.00:.2f})")

if __name__ == '__main__':
    test_price_calculation()
