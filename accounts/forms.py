from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'Seu nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'Seu sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'seu@email.com'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control bg-dark text-light border-secundary',
                'placeholder': 'Digite sua senha'
            })
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['password1'].widget.attrs.update({
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'Digite sua senha'
            })
            self.fields['password2'].widget.attrs.update({
                'class': 'form-control bg-dark text-light border-secondary',
                'placeholder': 'Confirme sua senha'
            })

    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(password) < 8:
            raise forms.ValidationError('A senha precisa ter pelo menos 8 caracteres.')
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('O email já está em uso.')
        return email
