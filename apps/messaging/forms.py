from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Type your message here...',
                'class': 'form-control'
            }),
            'attachment': forms.FileInput(attrs={'class': 'form-control'})
        }