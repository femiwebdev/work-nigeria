from django.contrib import admin
from .models import Project, ProjectProposal, ProjectMilestone, ProjectView

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'project_type', 'status', 'created_at']
    list_filter = ['project_type', 'status', 'experience_level', 'featured', 'urgent']
    search_fields = ['title', 'description', 'client__username']
    filter_horizontal = ['skills_required']
    date_hierarchy = 'created_at'

@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ['project', 'freelancer', 'proposed_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__title', 'freelancer__username']

@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'amount', 'due_date', 'status']
    list_filter = ['status', 'due_date']
    search_fields = ['project__title', 'title']

@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['project__title', 'user__username']