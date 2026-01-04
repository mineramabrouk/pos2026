from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportsIndexView.as_view(), name='reports_index'),
    path('financial/', views.FinancialReportView.as_view(), name='financial_report'),
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('inventory/', views.InventoryReportView.as_view(), name='inventory_report'),
]
