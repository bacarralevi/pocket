# accounts/urls.py

from django.urls import path #type: ignore
from . import views
from .views import set_budget

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    
    # Transaction URLs
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/create/', views.create_transaction, name='create_transaction'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    
    
    # Budget URLs
    path('set-budget/', views.set_budget, name='set_budget'),
    path('export_csv/', views.export_transactions_csv, name='export_transactions_csv'),
]
