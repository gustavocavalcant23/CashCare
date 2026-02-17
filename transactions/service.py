# transactions/services.py
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Transaction


class DashboardService:
    def __init__(self, user):
        self.user = user
        self.today = timezone.now().date()
        self.first_day_month = self.today.replace(day=1)
    
    def get_monthly_income(self):
        return self.user.transactions.filter(
            type=Transaction.Type.INCOME,
            is_completed=True,
            date__month=self.today.month,
            date__year=self.today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    def get_monthly_expense(self):
        return self.user.transactions.filter(
            type=Transaction.Type.EXPENSE,
            is_completed=True,
            date__month=self.today.month,
            date__year=self.today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    def get_monthly_savings(self):
        return self.get_monthly_income() - self.get_monthly_expense()
    
    def get_last_30_days_labels(self):
        return [(self.today - timedelta(days=i)).strftime('%d/%m') 
                for i in range(29, -1, -1)]
    
    def get_last_30_days_balance(self):
        start_date = self.today - timedelta(days=29)
        
        transactions = self.user.transactions.filter(
            is_completed=True,
            date__gte=start_date,
            date__lte=self.today
        ).order_by('date')
        
        daily_balance = []
        current_balance = 0
        current_date = start_date
        
        balance_before = self.user.transactions.filter(
            is_completed=True,
            date__lt=start_date
        ).aggregate(
            total=Sum('amount', field='CASE WHEN type="IN" THEN amount ELSE -amount END')
        )['total'] or 0
        
        for i in range(30):
            day = start_date + timedelta(days=i)
            # Transações deste dia
            day_transactions = [t for t in transactions if t.date == day]
            day_total = sum(t.signed_amount for t in day_transactions)
            
            if i == 0:
                current_balance = balance_before + day_total
            else:
                current_balance += day_total
            
            daily_balance.append(float(current_balance))
        
        return daily_balance
    
    def get_expenses_by_category(self):
        return self.user.transactions.filter(
            type=Transaction.Type.EXPENSE,
            is_completed=True,
            date__month=self.today.month,
            date__year=self.today.year
        ).values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
    
    def get_recent_transactions(self, limit=5):
        return self.user.transactions.filter(
            is_completed=True
        ).select_related('user').order_by('-date', '-created_at')[:limit]