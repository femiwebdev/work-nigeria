from django.urls import path
from . import views

app_name = 'gigs'

urlpatterns = [
    path('', views.GigListView.as_view(), name='gig_list'),
    path('create/', views.GigCreateView.as_view(), name='gig_create'),
    path('my-gigs/', views.my_gigs, name='my_gigs'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<int:pk>/', views.GigDetailView.as_view(), name='gig_detail'),
    path('<int:gig_id>/order/', views.order_gig, name='order_gig'),
    path('<int:gig_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/deliver/', views.deliver_order, name='deliver_order'),
]