from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Project, ProjectProposal, ProjectMilestone
from .forms import ProjectForm, ProjectProposalForm, MilestoneForm
from apps.accounts.models import Skill

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Project.objects.filter(status='open').select_related('client').prefetch_related('skills_required')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(skills_required__name__icontains=search)
            ).distinct()
        
        # Filter by skills
        skills = self.request.GET.getlist('skills')
        if skills:
            queryset = queryset.filter(skills_required__id__in=skills)
        
        # Filter by project type
        project_type = self.request.GET.get('project_type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Filter by experience level
        experience_level = self.request.GET.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Filter by budget range
        budget_min = self.request.GET.get('budget_min')
        budget_max = self.request.GET.get('budget_max')
        if budget_min:
            queryset = queryset.filter(budget_min__gte=budget_min)
        if budget_max:
            queryset = queryset.filter(budget_max__lte=budget_max)
        
        return queryset.annotate(proposal_count=Count('proposals'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = Skill.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['proposals'] = project.proposals.select_related('freelancer').order_by('-created_at')
        context['user_proposal'] = None
        
        if self.request.user.is_authenticated:
            try:
                context['user_proposal'] = project.proposals.get(freelancer=self.request.user)
            except ProjectProposal.DoesNotExist:
                pass
        
        # Track project view
        if self.request.user.is_authenticated:
            from .models import ProjectView
            ProjectView.objects.get_or_create(
                project=project,
                user=self.request.user,
                ip_address=self.get_client_ip(),
                defaults={'ip_address': self.get_client_ip()}
            )
        
        return context
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create.html'
    success_url = reverse_lazy('projects:my_projects')
    
    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

@login_required
def submit_proposal(request, project_id):
    project = get_object_or_404(Project, id=project_id, status='open')
    
    # Check if user already submitted a proposal
    if ProjectProposal.objects.filter(project=project, freelancer=request.user).exists():
        messages.warning(request, 'You have already submitted a proposal for this project.')
        return redirect('projects:project_detail', pk=project_id)
    
    if request.method == 'POST':
        form = ProjectProposalForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = request.user
            proposal.save()
            messages.success(request, 'Your proposal has been submitted successfully!')
            return redirect('projects:project_detail', pk=project_id)
    else:
        form = ProjectProposalForm()
    
    return render(request, 'projects/submit_proposal.html', {
        'form': form,
        'project': project
    })

@login_required
def my_projects(request):
    user = request.user
    
    # Projects posted by user (if client)
    posted_projects = Project.objects.filter(client=user).annotate(
        proposal_count=Count('proposals')
    ).order_by('-created_at')
    
    # Projects user has proposals on (if freelancer)
    proposal_projects = Project.objects.filter(
        proposals__freelancer=user
    ).select_related('client').order_by('-created_at')
    
    # Active projects (assigned to user)
    active_projects = Project.objects.filter(
        assigned_freelancer=user,
        status='in_progress'
    ).select_related('client').order_by('-updated_at')
    
    context = {
        'posted_projects': posted_projects,
        'proposal_projects': proposal_projects,
        'active_projects': active_projects,
    }
    return render(request, 'projects/my_projects.html', context)

@login_required
def manage_proposals(request, project_id):
    project = get_object_or_404(Project, id=project_id, client=request.user)
    proposals = project.proposals.select_related('freelancer').order_by('-created_at')
    
    return render(request, 'projects/manage_proposals.html', {
        'project': project,
        'proposals': proposals
    })

@login_required
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(ProjectProposal, id=proposal_id, project__client=request.user)
    
    if proposal.project.status == 'open':
        proposal.status = 'accepted'
        proposal.save()
        
        # Update project status and assign freelancer
        proposal.project.status = 'in_progress'
        proposal.project.assigned_freelancer = proposal.freelancer
        proposal.project.save()
        
        # Reject other proposals
        ProjectProposal.objects.filter(
            project=proposal.project
        ).exclude(id=proposal.id).update(status='rejected')
        
        messages.success(request, f'Proposal from {proposal.freelancer.username} has been accepted!')
    else:
        messages.error(request, 'This project is no longer available.')
    
    return redirect('projects:manage_proposals', project_id=proposal.project.id)