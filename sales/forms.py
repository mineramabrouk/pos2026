from django import forms
from .models import StockMovement, ExchangeRate, Category, Product, CashTransaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre de la Categoría',
            'description': 'Descripción',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'cost', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        reason = cleaned_data.get('reason')

        if movement_type == 'OUT' and not reason:
            self.add_error('reason', 'Es necesario un comentario explicando la reducción de stock.')
        
        return cleaned_data

class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = ['rate']
        labels = {
            'rate': 'Tipo de Cambio (BOB/USD)',
        }
        widgets = {
            'rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'cost', 'stock', 'barcode', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CashTransactionForm(forms.ModelForm):
    class Meta:
        model = CashTransaction
        fields = ['type', 'description', 'amount']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mantenimiento preventivo, Compra de insumos'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
