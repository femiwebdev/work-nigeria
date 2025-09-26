from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Skill

User = get_user_model()

class Project(models.Model):
    PROJECT_TYPES = (
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_projects')
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPES)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    hourly_rate_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=100, help_text="e.g., 1 week, 2 months")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    skills_required = models.ManyToManyField(Skill, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    featured = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)
    location_required = models.CharField(max_length=100, blank=True)
    remote_ok = models.BooleanField(default=True)
    attachments = models.FileField(upload_to='project_attachments/', blank=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_freelancer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_budget_display(self):
        if self.project_type == 'fixed':
            if self.budget_min and self.budget_max:
                return f"₦{self.budget_min:,.0f} - ₦{self.budget_max:,.0f}"
            elif self.budget_min:
                return f"₦{self.budget_min:,.0f}+"
        else:
            if self.hourly_rate_min and self.hourly_rate_max:
                return f"₦{self.hourly_rate_min}/hr - ₦{self.hourly_rate_max}/hr"
            elif self.hourly_rate_min:
                return f"₦{self.hourly_rate_min}/hr+"
        return "Budget not specified"

class ProjectProposal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_duration = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attachments = models.FileField(upload_to='proposal_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('project', 'freelancer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.freelancer.username} - {self.project.title}"

class ProjectMilestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deliverables = models.FileField(upload_to='milestone_deliverables/', blank=True, null=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"

class ProjectView(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'user', 'ip_address')