from django.views.generic import ListView
from sales.models import Product

class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.filter(stock__gt=0).order_by('name')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query) | queryset.filter(category__name__icontains=query)
            queryset = queryset.distinct()
        return queryset

def about(request):
    from django.shortcuts import render
    return render(request, 'catalog/about.html')

def contact(request):
    from django.shortcuts import render, redirect
    from django.contrib import messages
    
    if request.method == 'POST':
        # Here you would typically send the email
        # name = request.POST.get('name')
        # email = request.POST.get('email')
        # subject = request.POST.get('subject')
        # message = request.POST.get('message')
        
        # For now, just show a success message
        messages.success(request, '¡Tu mensaje ha sido enviado exitosamente! Nos pondremos en contacto contigo pronto.')
        return redirect('contact')
        
    return render(request, 'catalog/contact.html')

