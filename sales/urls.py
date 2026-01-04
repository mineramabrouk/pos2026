from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/import/', views.ImportProductsView.as_view(), name='import_products'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('products/<int:pk>/stock/', views.StockMovementCreateView.as_view(), name='stock_movement_add'),
    path('config/exchange-rate/', views.ExchangeRateView.as_view(), name='exchange_rate'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('api/sales/create/', views.create_sale, name='create_sale'),
    path('receipt/<str:receipt_number>/', views.ReceiptView.as_view(), name='receipt'),
    path('cash-transaction/add/', views.CashTransactionCreateView.as_view(), name='add_cash_transaction'),
]
