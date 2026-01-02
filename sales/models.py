from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class ExchangeRate(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=4, help_text="Bolivianos per USD")
    date_set = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"1 USD = {self.rate} BOB ({self.date_set.strftime('%Y-%m-%d %H:%M')})"

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Categoría")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Bolivianos", verbose_name="Precio (BOB)")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost in Bolivianos", verbose_name="Costo (BOB)")
    stock = models.IntegerField(default=0, verbose_name="Stock")
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Código de Barras")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagen")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price in USD (Auto-calculated)", verbose_name="Precio (USD)")

    def save(self, *args, **kwargs):
        # Calculate price_usd based on the latest ExchangeRate
        latest_rate = ExchangeRate.objects.order_by('-date_set').first()
        if latest_rate and self.price:
            self.price_usd = self.price / latest_rate.rate
        else:
            self.price_usd = None # Or keep previous value if desired, but None is safer if no rate exists
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Sale(models.Model):
    salesperson = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales')
    date_added = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Simple receipt number generation (can be improved)
            last_sale = Sale.objects.all().order_by('id').last()
            if last_sale:
                self.receipt_number = f"REC-{last_sale.id + 1:06d}"
            else:
                self.receipt_number = "REC-000001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.receipt_number} by {self.salesperson.username}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit price at time of sale")
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name="Producto")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name="Tipo de Movimiento")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Costo de adquisición (solo para entradas)", verbose_name="Costo Unitario (BOB)")
    reason = models.TextField(blank=True, null=True, verbose_name="Razón/Comentario")
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuario")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    def save(self, *args, **kwargs):
        # Update product stock
        if not self.pk:  # Only on creation
            if self.movement_type == 'IN':
                self.product.stock += self.quantity
                # Optionally update product cost if provided
                if self.cost:
                    self.product.cost = self.cost
            elif self.movement_type == 'OUT':
                self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
