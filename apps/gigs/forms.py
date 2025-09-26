from django import forms
from .models import Gig, GigOrder, GigDelivery, GigCategory
from apps.accounts.models import Skill

class GigForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Gig
        fields = [
            'title', 'description', 'category', 'skills',
            'basic_price', 'basic_description', 'basic_delivery_time', 'basic_revisions',
            'standard_price', 'standard_description', 'standard_delivery_time', 'standard_revisions',
            'premium_price', 'premium_description', 'premium_delivery_time', 'premium_revisions',
            'extra_fast_delivery', 'extra_fast_price'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'basic_description': forms.Textarea(attrs={'rows': 4}),
            'standard_description': forms.Textarea(attrs={'rows': 4}),
            'premium_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['skills', 'extra_fast_delivery']:
                field.widget.attrs.update({'class': 'form-control'})

class GigOrderForm(forms.ModelForm):
    fast_delivery = forms.BooleanField(required=False, label="Fast Delivery (+24 hours)")
    
    class Meta:
        model = GigOrder
        fields = ['package', 'requirements', 'fast_delivery']
        widgets = {
            'requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please provide detailed requirements for your order...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.gig = kwargs.pop('gig', None)
        super().__init__(*args, **kwargs)
        
        # Update package choices based on available packages
        if self.gig:
            package_choices = [('basic', f'Basic - ₦{self.gig.basic_price}')]
            if self.gig.standard_price:
                package_choices.append(('standard', f'Standard - ₦{self.gig.standard_price}'))
            if self.gig.premium_price:
                package_choices.append(('premium', f'Premium - ₦{self.gig.premium_price}'))
            
            self.fields['package'].choices = package_choices
            
            # Show fast delivery option only if available
            if not self.gig.extra_fast_delivery:
                del self.fields['fast_delivery']
        
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-control'})

class GigDeliveryForm(forms.ModelForm):
    class Meta:
        model = GigDelivery
        fields = ['message', 'files']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your delivery...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})