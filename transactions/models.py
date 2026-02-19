from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Transaction(models.Model):
    class Category(models.TextChoices):
        ALIMENTACAO = 'ALM', 'Alimentação'
        TRANSPORTE = 'TRP', 'Transporte'
        MORADIA = 'MOR', 'Moradia'
        SAUDE = 'SAU', 'Saúde'
        EDUCACAO = 'EDU', 'Educação'
        LAZER = 'LAZ', 'Lazer'
        COMPRAS = 'COM', 'Compras'
        SALARIO = 'SAL', 'Salário'
        INVESTIMENTO = 'INV', 'Investimento'
        OUTROS = 'OUT', 'Outros'

    class Type(models.TextChoices):
        INCOME = 'IN', 'Entrada'
        EXPENSE = 'OUT', 'Saída'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField('Título', max_length=120)
    description = models.TextField('Descrição', max_length=255, blank=True)
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    type = models.CharField('Tipo', max_length=3, choices=Type.choices, default=Type.EXPENSE)
    category = models.CharField('Categoria', max_length=3, choices=Category.choices, default=Category.OUTROS)
    is_completed = models.BooleanField('Concluída', default=False)
    date = models.DateField('Data')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return f"{self.title} - {self.get_type_display()} R$ {self.amount}"

    @property
    def status(self):
        if self.is_completed:
            return 'Pago/Recebido'
        elif self.date > timezone.now().date():
            return 'Agendado'
        else:
            return 'Pendente'

    @property
    def signed_amount(self):
        return self.amount if self.type == self.Type.INCOME else -self.amount
