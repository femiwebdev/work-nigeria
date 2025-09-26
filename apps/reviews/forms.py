from django import forms
from .models import Review, ReviewResponse

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'communication', 'quality', 'timeliness', 'is_public']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'communication': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'quality': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'timeliness': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share your experience...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-control'})

class ReviewResponseForm(forms.ModelForm):
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Respond to this review...',
                'class': 'form-control'
            }),
        }