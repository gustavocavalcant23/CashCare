from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'category', 'amount', 'is_completed')
    search_fields = ('user', 'title', 'description')
    list_filter = ('user', 'type', 'category', 'is_completed')
