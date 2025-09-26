from django import forms
from .models import Project, ProjectProposal, ProjectMilestone
from apps.accounts.models import Skill

class ProjectForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'project_type', 'budget_min', 'budget_max',
            'hourly_rate_min', 'hourly_rate_max', 'duration', 'experience_level',
            'skills_required', 'location_required', 'remote_ok', 'attachments',
            'deadline', 'urgent'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['skills_required', 'remote_ok', 'urgent']:
                field.widget.attrs.update({'class': 'form-control'})

class ProjectProposalForm(forms.ModelForm):
    class Meta:
        model = ProjectProposal
        fields = ['cover_letter', 'proposed_amount', 'proposed_duration', 'attachments']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Explain why you are the best fit for this project...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'amount', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})