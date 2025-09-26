# The file /work-nigeria/work-nigeria/apps/payments/__init__.py is intentionally left blank.

from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class PaymentMethod(models.Model):
    PROVIDER_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
    )
    
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('payment', 'Payment'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
        ('commission', 'Commission'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    reference = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # External payment provider details
    provider_reference = models.CharField(max_length=200, blank=True)
    provider_response = models.JSONField(null=True, blank=True)
    
    # Related objects
    gig_order = models.ForeignKey('gigs.GigOrder', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reference} - {self.user.username} - ₦{self.amount}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - ₦{self.balance}"
    
    def add_funds(self, amount, description=""):
        """Add funds to available balance"""
        self.balance += Decimal(str(amount))
        self.total_earned += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            reference=f"ADD_{self.user.id}_{int(timezone.now().timestamp())}",
            user=self.user,
            transaction_type='payment',
            amount=amount,
            status='completed',
            description=description
        )
    
    def add_pending_funds(self, amount):
        """Add funds to pending balance (escrow)"""
        self.pending_balance += Decimal(str(amount))
        self.save()
    
    def release_pending_funds(self, amount):
        """Move funds from pending to available balance"""
        if self.pending_balance >= amount:
            self.pending_balance -= Decimal(str(amount))
            self.balance += Decimal(str(amount))
            self.total_earned += Decimal(str(amount))
            self.save()
            return True
        return False
    
    def withdraw_funds(self, amount):
        """Withdraw funds from available balance"""
        if self.balance >= amount:
            self.balance -= Decimal(str(amount))
            self.total_withdrawn += Decimal(str(amount))
            self.save()
            return True
        return False

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    WITHDRAWAL_METHODS = (
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('paypal', 'PayPal'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=WITHDRAWAL_METHODS)
    account_details = models.JSONField()  # Store bank account or payment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ₦{self.amount} ({self.status})"

class EscrowPayment(models.Model):
    """Handles escrow payments for projects and gigs"""
    STATUS_CHOICES = (
        ('held', 'Held in Escrow'),
        ('released', 'Released to Freelancer'),
        ('refunded', 'Refunded to Client'),
        ('disputed', 'In Dispute'),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='escrow')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_payments')
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='held')
    
    # Release conditions
    auto_release_date = models.DateTimeField(null=True, blank=True)
    manual_release = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Escrow: ₦{self.amount} ({self.status})"
    
    def release_payment(self):
        """Release payment to freelancer"""
        if self.status == 'held':
            # Calculate amount after commission
            freelancer_amount = self.amount - self.commission
            
            # Add to freelancer's wallet
            wallet, created = Wallet.objects.get_or_create(user=self.payee)
            wallet.release_pending_funds(freelancer_amount)
            
            # Update status
            self.status = 'released'
            self.released_at = timezone.now()
            self.save()
            
            # Create commission transaction
            Transaction.objects.create(
                reference=f"COMM_{self.id}_{int(timezone.now().timestamp())}",
                user=self.payee,
                transaction_type='commission',
                amount=-self.commission,
                status='completed',
                description=f"Platform commission for escrow payment #{self.id}"
            )
            
            return True
        return False