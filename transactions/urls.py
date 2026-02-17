from django.urls import path

from . import views


urlpatterns = [

    path('', views.DashboardView.as_view(), name='dashboard'),
    path('add/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:pk>/update', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/complete', views.TransctionCompleteView.as_view(), name='transaction_complete'),
    path('transactions/<int:pk>/delete', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),

]
