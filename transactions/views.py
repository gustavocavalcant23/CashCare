import json
from datetime import timedelta

from django.views.generic import TemplateView, CreateView, ListView, UpdateView, View
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .service import DashboardService
from .models import Transaction
from .forms import TransactionForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        service = DashboardService(user)

        context.update({
            'name': f'{user.first_name} {user.last_name}',
            'current_balance': user.balance,
            'monthly_incomes': service.get_monthly_income(),
            'monthly_expenses': service.get_monthly_expense(),
            'monthly_savings': service.get_monthly_savings(),
        })

        context['grafico_linha_labels'] = json.dumps(service.get_last_30_days_labels())
        context['grafico_linha_data'] = json.dumps(service.get_last_30_days_balance())
        
        category = service.get_expenses_by_category()

        context['categorias_labels'] = json.dumps([c['category'] for c in category])
        context['categorias_data'] = json.dumps([float(c['total']) for c in category])
        
        context['ultimas_transacoes'] = service.get_recent_transactions(5)
        
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_create.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        period = self.request.GET.get('period', '')
        today = timezone.now().date()
        
        period_days = {
            '7': 7, '15': 15, '30': 30, '45': 45, '60': 60,
        }
        
        if period in period_days:
            start_date = today - timedelta(days=period_days[period])
            queryset = queryset.filter(date__gte=start_date, date__lte=today)
        
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        if start_date and end_date:
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)

        elif start_date:
            queryset = queryset.filter(date__gte=start_date)

        elif end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        tipos_selecionados = []

        if self.request.GET.get('type_in'):
            tipos_selecionados.append('IN')

        if self.request.GET.get('type_out'):
            tipos_selecionados.append('OUT')
        
        if tipos_selecionados:
            queryset = queryset.filter(type__in=tipos_selecionados)
        
        status_selecionados = []

        if self.request.GET.get('status_completed'):
            status_selecionados.append(True)

        if self.request.GET.get('status_pending'):
            status_selecionados.append(False)
        
        if status_selecionados:
            queryset = queryset.filter(is_completed__in=status_selecionados)
        
        categorias = self.request.GET.getlist('category')

        if categorias:
            queryset = queryset.filter(category__in=categorias)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['search'] = self.request.GET.get('search', '')
        context['current_period'] = self.request.GET.get('period', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        context['selected_types'] = []

        if self.request.GET.get('type_in'):
            context['selected_types'].append('IN')

        if self.request.GET.get('type_out'):
            context['selected_types'].append('OUT')
        
        context['selected_status'] = []

        if self.request.GET.get('status_completed'):
            context['selected_status'].append('completed')

        if self.request.GET.get('status_pending'):
            context['selected_status'].append('pending')
        
        context['selected_categories'] = self.request.GET.getlist('category')
        
        filtros_ativos = 0

        if context['search']: filtros_ativos += 1
        if context['current_period']: filtros_ativos += 1
        if context['current_period'] == 'custom': filtros_ativos -= 1
        if context['start_date'] or context['end_date']: filtros_ativos += 1
        if context['selected_types']: filtros_ativos += 1
        if context['selected_status']: filtros_ativos += 1
        if context['selected_categories']: filtros_ativos += 1
        
        context['total_filtros_ativos'] = filtros_ativos
        
        context['categorias'] = Transaction.Category.choices

        return context
    

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    template_name = 'transactions/transaction_update.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')


class TransctionCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

        transaction.is_completed = True
        transaction.save()

        return redirect('transaction_list')
    

class TransactionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
        transaction.delete()

        return redirect('transaction_list')


@login_required
def calendar_view(request, year=None, month=None):
    today = timezone.now()
    year = year or today.year
    month = month or today.month
    
    year = int(year)
    month = int(month)
    
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )
    
    days_data = {}
    for t in transactions:
        day = t.date.day
        if day not in days_data:
            days_data[day] = {'completed': 0, 'pending': 0}
        
        if t.is_completed:
            days_data[day]['completed'] += 1
        else:
            days_data[day]['pending'] += 1
    
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    context = {
        'year': year,
        'month': month,
        'month_name': meses[month - 1],
        'days_data': json.dumps(days_data),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'transactions/calendar.html', context)
