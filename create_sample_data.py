import os
import sys
import django
import shutil
from django.core.files import File
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_project.settings')
django.setup()

from sales.models import Category, Product, ExchangeRate

# Artifacts directory where images were saved
ARTIFACTS_DIR = r"C:\Users\Dero.DESKTOP-G546ADK\.gemini\antigravity\brain\499d5156-ecd2-4a13-8bfe-9778aa2efc26"

from decimal import Decimal

# Define data
DATA = [
    {
        "category": "Electronics",
        "products": [
            {
                "name": "Laptop Pro X",
                "price": Decimal("8500.00"),
                "cost": Decimal("6000.00"),
                "stock": 15,
                "barcode": "ELEC001",
                "image_filename": "laptop_product_1767311008811.png"
            },
            {
                "name": "Smartphone Z",
                "price": Decimal("3500.00"),
                "cost": Decimal("2500.00"),
                "stock": 30,
                "barcode": "ELEC002",
                "image_filename": "smartphone_product_1767311021812.png"
            },
            {
                "name": "Wireless Headphones",
                "price": Decimal("850.00"),
                "cost": Decimal("500.00"),
                "stock": 50,
                "barcode": "ELEC003",
                "image_filename": "headphones_product_1767311036889.png"
            }
        ]
    },
    {
        "category": "Beverages",
        "products": [
            {
                "name": "Cola Classic",
                "price": Decimal("12.00"),
                "cost": Decimal("8.00"),
                "stock": 200,
                "barcode": "BEV001",
                "image_filename": "cola_product_1767311049040.png"
            },
            {
                "name": "Fresh Orange Juice",
                "price": Decimal("15.00"),
                "cost": Decimal("9.00"),
                "stock": 50,
                "barcode": "BEV002",
                "image_filename": "orange_juice_product_1767311061474.png"
            },
            {
                "name": "Mineral Water",
                "price": Decimal("8.00"),
                "cost": Decimal("4.00"),
                "stock": 300,
                "barcode": "BEV003",
                "image_filename": "water_bottle_product_1767311075058.png"
            }
        ]
    },
    {
        "category": "Snacks",
        "products": [
            {
                "name": "Potato Chips",
                "price": Decimal("10.00"),
                "cost": Decimal("6.00"),
                "stock": 100,
                "barcode": "SNK001",
                "image_filename": None # Quota limit
            },
            {
                "name": "Chocolate Bar",
                "price": Decimal("7.00"),
                "cost": Decimal("4.00"),
                "stock": 150,
                "barcode": "SNK002",
                "image_filename": None # Quota limit
            },
            {
                "name": "Cookies Pack",
                "price": Decimal("18.00"),
                "cost": Decimal("12.00"),
                "stock": 80,
                "barcode": "SNK003",
                "image_filename": None # Quota limit
            }
        ]
    }
]

def create_data():
    # Create Exchange Rate if not exists
    if not ExchangeRate.objects.exists():
        ExchangeRate.objects.create(rate=6.96)
        print("Created default Exchange Rate (6.96)")

    for cat_data in DATA:
        category, created = Category.objects.get_or_create(name=cat_data["category"])
        if created:
            print(f"Created Category: {category.name}")
        else:
            print(f"Category exists: {category.name}")

        for prod_data in cat_data["products"]:
            # Check if product exists
            if Product.objects.filter(barcode=prod_data["barcode"]).exists():
                print(f"Product exists: {prod_data['name']}")
                continue

            product = Product(
                name=prod_data["name"],
                category=category,
                price=prod_data["price"],
                cost=prod_data["cost"],
                stock=prod_data["stock"],
                barcode=prod_data["barcode"]
            )

            # Handle Image
            if prod_data["image_filename"]:
                src_path = Path(ARTIFACTS_DIR) / prod_data["image_filename"]
                if src_path.exists():
                    with open(src_path, 'rb') as f:
                        product.image.save(prod_data["image_filename"], File(f), save=False)
                else:
                    print(f"Warning: Image not found at {src_path}")

            product.save()
            print(f"Created Product: {product.name}")

if __name__ == "__main__":
    create_data()
