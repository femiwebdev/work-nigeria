from django import forms
from .models import WithdrawalRequest

class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'method', 'account_details']
        widgets = {
            'account_details': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your account details (Account number, Bank name, etc.)'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.user and hasattr(self.user, 'wallet'):
            if amount > self.user.wallet.balance:
                raise forms.ValidationError('Insufficient funds in wallet.')
        if amount < 1000:  # Minimum withdrawal amount
            raise forms.ValidationError('Minimum withdrawal amount is ₦1,000.')
        return amount