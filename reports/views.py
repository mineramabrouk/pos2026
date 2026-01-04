from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from sales.models import Sale, CashTransaction, Product
from datetime import timedelta

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()

class ReportsIndexView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'reports/index.html'

class FinancialReportView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'reports/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filters
        date_range = self.request.GET.get('date_range', 'today')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        # Base QuerySets
        sales = Sale.objects.all()
        transactions = CashTransaction.objects.all()

        # Date Filtering
        today = timezone.now().date()
        if date_range == 'today':
            sales = sales.filter(date_added__date=today)
            transactions = transactions.filter(date=today)
        elif date_range == 'week':
            start_week = today - timedelta(days=today.weekday())
            sales = sales.filter(date_added__date__gte=start_week)
            transactions = transactions.filter(date__gte=start_week)
        elif date_range == 'month':
            sales = sales.filter(date_added__year=today.year, date_added__month=today.month)
            transactions = transactions.filter(date__year=today.year, date__month=today.month)
        elif date_range == 'year':
            sales = sales.filter(date_added__year=today.year)
            transactions = transactions.filter(date__year=today.year)
        elif date_range == 'custom' and start_date_str and end_date_str:
            sales = sales.filter(date_added__date__range=[start_date_str, end_date_str])
            transactions = transactions.filter(date__range=[start_date_str, end_date_str])
        
        # 1. Total Sales
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # 2. Cash Transactions
        cash_in = transactions.filter(type='IN').aggregate(total=Sum('amount'))['total'] or 0
        cash_out = transactions.filter(type='OUT').aggregate(total=Sum('amount'))['total'] or 0
        
        # 3. Net Balance
        net_balance = float(total_sales) + float(cash_in) - float(cash_out)
        
        # 4. Recent Transactions for display (filtered)
        recent_sales = sales.order_by('-date_added')[:10]
        recent_cash_movements = transactions.order_by('-date')[:10]

        context.update({
            'total_sales': total_sales,
            'cash_in': cash_in,
            'cash_out': cash_out,
            'net_balance': net_balance,
            'recent_sales': recent_sales,
            'recent_cash_movements': recent_cash_movements,
            'current_filters': {
                'date_range': date_range,
                'is_today': date_range == 'today',
                'is_week': date_range == 'week',
                'is_month': date_range == 'month',
                'is_year': date_range == 'year',
                'is_custom': date_range == 'custom',
                'start_date': start_date_str,
                'end_date': end_date_str,
            }
        })
        return context

class SalesReportView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'reports/sales_report_fixed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filters
        date_range = self.request.GET.get('date_range', 'today')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        salesperson_id = self.request.GET.get('salesperson')

        sales = Sale.objects.all().order_by('-date_added')
        
        # Date Filtering
        today = timezone.now().date()
        if date_range == 'today':
            sales = sales.filter(date_added__date=today)
        elif date_range == 'week':
            start_week = today - timedelta(days=today.weekday())
            sales = sales.filter(date_added__date__gte=start_week)
        elif date_range == 'month':
            sales = sales.filter(date_added__year=today.year, date_added__month=today.month)
        elif date_range == 'custom' and start_date_str and end_date_str:
            sales = sales.filter(date_added__date__range=[start_date_str, end_date_str])

        # Salesperson Filtering
        if salesperson_id and salesperson_id != 'all':
            sales = sales.filter(salesperson_id=salesperson_id)

        # Calculate Total for filtered sales
        total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0

        # Prepare salespeople with selection state
        salespeople = []
        for user in User.objects.all():
            user.is_selected = (user.id == int(salesperson_id)) if salesperson_id and salesperson_id != 'all' else False
            salespeople.append(user)

        context.update({
            'sales': sales,
            'total_sales': total_sales,
            'salespeople': salespeople,
            'current_filters': {
                'date_range': date_range,
                'is_today': date_range == 'today',
                'is_week': date_range == 'week',
                'is_month': date_range == 'month',
                'is_custom': date_range == 'custom',
                'start_date': start_date_str,
                'end_date': end_date_str,
                'salesperson': salesperson_id and int(salesperson_id) if salesperson_id != 'all' and salesperson_id else 'all'
            }
        })
        return context

class InventoryReportView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'reports/inventory_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all().order_by('name')
        return context
