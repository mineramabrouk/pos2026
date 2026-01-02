from django import forms
from .models import StockMovement, ExchangeRate, Category

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
