from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import json
import uuid
from .models import Transaction, Wallet, WithdrawalRequest, PaymentMethod, EscrowPayment
from .forms import WithdrawalRequestForm
from .services import PaystackService, FlutterwaveService

@login_required
def wallet_dashboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    recent_transactions = Transaction.objects.filter(user=request.user)[:10]
    
    context = {
        'wallet': wallet,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'payments/wallet_dashboard.html', context)

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'payments/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

@login_required
def initiate_payment(request, order_id, order_type):
    """Initiate payment for gig order or project"""
    if order_type == 'gig':
        from apps.gigs.models import GigOrder
        order = get_object_or_404(GigOrder, id=order_id, buyer=request.user)
        amount = order.total_price
        description = f"Payment for gig: {order.gig.title}"
    elif order_type == 'project':
        from apps.projects.models import ProjectProposal
        proposal = get_object_or_404(ProjectProposal, id=order_id, status='accepted')
        amount = proposal.proposed_amount
        description = f"Payment for project: {proposal.project.title}"
        order = proposal
    else:
        messages.error(request, 'Invalid order type.')
        return redirect('payments:wallet_dashboard')
    
    # Calculate commission
    commission = amount * settings.PLATFORM_COMMISSION_RATE
    
    # Create transaction
    reference = f"PAY_{order_type.upper()}_{order_id}_{uuid.uuid4().hex[:8]}"
    transaction = Transaction.objects.create(
        reference=reference,
        user=request.user,
        transaction_type='payment',
        amount=amount,
        description=description,
        **{f'{order_type}_order' if order_type == 'gig' else 'project': order}
    )
    
    # Create escrow payment
    payee = order.gig.freelancer if order_type == 'gig' else order.project.assigned_freelancer
    EscrowPayment.objects.create(
        transaction=transaction,
        payer=request.user,
        payee=payee,
        amount=amount,
        commission=commission,
        auto_release_date=timezone.now() + timezone.timedelta(days=14)
    )
    
    # Initialize payment with Paystack
    paystack = PaystackService()
    payment_url = paystack.initialize_payment(
        email=request.user.email,
        amount=int(amount * 100),  # Paystack expects amount in kobo
        reference=reference,
        callback_url=request.build_absolute_uri('/payments/verify/')
    )
    
    if payment_url:
        return redirect(payment_url)
    else:
        messages.error(request, 'Failed to initialize payment. Please try again.')
        return redirect('payments:wallet_dashboard')

@csrf_exempt
def verify_payment(request):
    """Verify payment from Paystack"""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('payments:wallet_dashboard')
    
    try:
        transaction = Transaction.objects.get(reference=reference)
    except Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found.')
        return redirect('payments:wallet_dashboard')
    
    # Verify with Paystack
    paystack = PaystackService()
    verification_result = paystack.verify_payment(reference)
    
    if verification_result and verification_result.get('status') == 'success':
        transaction.status = 'completed'
        transaction.provider_reference = verification_result.get('id')
        transaction.provider_response = verification_result
        transaction.completed_at = timezone.now()
        transaction.save()
        
        # Add funds to escrow (pending balance)
        if hasattr(transaction, 'escrow'):
            wallet, created = Wallet.objects.get_or_create(user=transaction.escrow.payee)
            wallet.add_pending_funds(transaction.amount - transaction.escrow.commission)
        
        messages.success(request, 'Payment completed successfully!')
        
        # Update order status
        if transaction.gig_order:
            transaction.gig_order.status = 'in_progress'
            transaction.gig_order.save()
        elif transaction.project:
            transaction.project.status = 'in_progress'
            transaction.project.save()
    else:
        transaction.status = 'failed'
        transaction.save()
        messages.error(request, 'Payment verification failed.')
    
    return redirect('payments:wallet_dashboard')

@login_required
def request_withdrawal(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = WithdrawalRequestForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            if wallet.balance >= amount:
                withdrawal_request = form.save(commit=False)
                withdrawal_request.user = request.user
                withdrawal_request.save()
                
                # Deduct from wallet
                wallet.withdraw_funds(amount)
                
                messages.success(request, 'Withdrawal request submitted successfully!')
                return redirect('payments:wallet_dashboard')
            else:
                messages.error(request, 'Insufficient funds.')
    else:
        form = WithdrawalRequestForm(user=request.user)
    
    return render(request, 'payments/request_withdrawal.html', {
        'form': form,
        'wallet': wallet
    })

@login_required
def withdrawal_history(request):
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/withdrawal_history.html', {'withdrawals': withdrawals})