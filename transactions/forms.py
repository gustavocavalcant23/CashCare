from django import forms
from django.utils import timezone

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['user']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control bg-dark text-light'}),
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-light', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):   
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields['date'].initial = today
        