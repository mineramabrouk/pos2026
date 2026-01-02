import os
import django
from django.template import Context, Template

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_project.settings')
django.setup()

from django.forms import modelform_factory
from sales.models import Product

def reproduce():
    ProductForm = modelform_factory(Product, fields=['name', 'category', 'price', 'cost', 'stock', 'barcode', 'image'])
    form = ProductForm()
    
    print("Rendering form fields:")
    for field in form:
        print(f"Field: {field.name}, Label: '{field.label}'")

if __name__ == "__main__":
    reproduce()
