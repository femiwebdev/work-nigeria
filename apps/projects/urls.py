from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:project_id>/submit-proposal/', views.submit_proposal, name='submit_proposal'),
    path('<int:project_id>/manage-proposals/', views.manage_proposals, name='manage_proposals'),
    path('proposal/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
]