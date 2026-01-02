from .models import Product, StockMovement, ExchangeRate, Category, Sale, SaleItem
from .forms import StockMovementForm, ExchangeRateForm, CategoryForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
import json

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()

class ProductListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Product
    template_name = 'sales/product_list.html'
    context_object_name = 'products'
    ordering = ['name']

class ProductCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Product
    template_name = 'sales/product_form.html'
    fields = ['name', 'category', 'price', 'cost', 'stock', 'barcode', 'image']
    success_url = reverse_lazy('product_list')

class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Product
    template_name = 'sales/product_form.html'
    fields = ['name', 'category', 'price', 'cost', 'stock', 'barcode', 'image']
    success_url = reverse_lazy('product_list')

class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'sales/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

class StockMovementCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'sales/stock_movement_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.product = self.product
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def get_success_url(self):
        return reverse_lazy('product_list')

class ExchangeRateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ExchangeRate
    form_class = ExchangeRateForm
    template_name = 'sales/exchange_rate.html'
    success_url = reverse_lazy('exchange_rate')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_rate'] = ExchangeRate.objects.order_by('-date_set').first()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        new_rate = form.instance.rate
        
        # Bulk update product prices
        products_updated = 0
        for product in Product.objects.all():
            if product.price_usd:
                product.price = product.price_usd * new_rate
                product.save()
                products_updated += 1
        
        messages.success(self.request, f'Tipo de cambio actualizado a {new_rate}. Se recalcularon los precios de {products_updated} productos.')
        return response

class CategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Category
    template_name = 'sales/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

class CategoryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'sales/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'sales/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'sales/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

class POSView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/pos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serialize products for JS
        products = Product.objects.filter(stock__gt=0).select_related('category')
        products_data = []
        for p in products:
            products_data.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'stock': p.stock,
                'category': p.category.name if p.category else 'Sin Categoría',
                'barcode': p.barcode,
                'image_url': p.image.url if p.image else '',
            })
        context['products_json'] = json.dumps(products_data)
        return context

@login_required
def create_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'success': False, 'error': 'El carrito está vacío.'})

            with transaction.atomic():
                # Create Sale
                sale = Sale.objects.create(
                    salesperson=request.user,
                    total_amount=0 # Will calculate
                )
                
                total_amount = 0
                
                for item in items:
                    product_id = item.get('id')
                    quantity = int(item.get('quantity', 0))
                    price = float(item.get('price', 0)) # Editable price
                    
                    if quantity <= 0:
                        continue
                        
                    product = Product.objects.select_for_update().get(pk=product_id)
                    
                    if product.stock < quantity:
                        raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {product.stock}")
                    
                    # Deduct stock
                    product.stock -= quantity
                    product.save()
                    
                    # Create SaleItem
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
                    
                    total_amount += price * quantity
                
                sale.total_amount = total_amount
                sale.save()
                
            return JsonResponse({'success': True, 'sale_id': sale.receipt_number})
            
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
            
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

class ReceiptView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/receipt.html'
    context_object_name = 'sale'
    slug_field = 'receipt_number'
    slug_url_kwarg = 'receipt_number'

