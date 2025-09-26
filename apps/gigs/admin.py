from django.contrib import admin
from .models import GigCategory, Gig, GigImage, GigOrder, GigDelivery, GigRevision, GigFavorite

@admin.register(GigCategory)
class GigCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ['title', 'freelancer', 'category', 'basic_price', 'is_active', 'rating', 'orders_completed']
    list_filter = ['category', 'is_active', 'featured', 'created_at']
    search_fields = ['title', 'description', 'freelancer__username']
    filter_horizontal = ['skills']

@admin.register(GigOrder)
class GigOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'gig', 'buyer', 'package', 'price', 'status', 'created_at']
    list_filter = ['status', 'package', 'created_at']
    search_fields = ['gig__title', 'buyer__username']

@admin.register(GigDelivery)
class GigDeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'delivered_at']
    search_fields = ['order__gig__title']