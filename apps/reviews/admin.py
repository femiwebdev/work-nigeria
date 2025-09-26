from django.contrib import admin
from .models import Review, ReviewResponse

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'rating', 'created_at', 'is_public']
    list_filter = ['rating', 'is_public', 'created_at']
    search_fields = ['reviewer__username', 'reviewee__username', 'title', 'comment']
    readonly_fields = ['created_at']

@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'created_at']
    search_fields = ['review__title', 'response_text']