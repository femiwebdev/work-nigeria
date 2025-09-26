from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('project/<int:project_id>/', views.project_conversation, name='project_conversation'),
    path('gig/<int:order_id>/', views.gig_conversation, name='gig_conversation'),
    path('send/<int:conversation_id>/', views.send_message_ajax, name='send_message_ajax'),
]