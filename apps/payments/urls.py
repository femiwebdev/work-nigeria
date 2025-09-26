from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('wallet/', views.wallet_dashboard, name='wallet_dashboard'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('pay/<int:order_id>/<str:order_type>/', views.initiate_payment, name='initiate_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('withdrawals/', views.withdrawal_history, name='withdrawal_history'),
]