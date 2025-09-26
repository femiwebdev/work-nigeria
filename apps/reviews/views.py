from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from .models import Review, ReviewResponse
from .forms import ReviewForm, ReviewResponseForm

@login_required
def create_review(request, order_id, order_type):
    """Create review for completed gig order or project"""
    if order_type == 'gig':
        from apps.gigs.models import GigOrder
        order = get_object_or_404(GigOrder, id=order_id, buyer=request.user, status='completed')
        reviewee = order.gig.freelancer
        
        # Check if review already exists
        if hasattr(order, 'review'):
            messages.info(request, 'You have already reviewed this order.')
            return redirect('gigs:order_detail', order_id=order_id)
            
    elif order_type == 'project':
        from apps.projects.models import Project
        project = get_object_or_404(Project, id=order_id, client=request.user, status='completed')
        reviewee = project.assigned_freelancer
        order = project
        
        # Check if review already exists
        if hasattr(project, 'review'):
            messages.info(request, 'You have already reviewed this project.')
            return redirect('projects:project_detail', pk=order_id)
    else:
        messages.error(request, 'Invalid order type.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = reviewee
            
            if order_type == 'gig':
                review.gig_order = order
            else:
                review.project = order
                
            review.save()
            
            # Update reviewee's rating
            update_user_rating(reviewee)
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('reviews:user_reviews', user_id=reviewee.id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'order': order,
        'reviewee': reviewee,
        'order_type': order_type,
    }
    return render(request, 'reviews/create_review.html', context)

def user_reviews(request, user_id):
    """Display all reviews for a specific user"""
    user = get_object_or_404(User, id=user_id)
    reviews = Review.objects.filter(reviewee=user, is_public=True).select_related('reviewer').order_by('-created_at')
    
    # Calculate statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id'),
        average_communication=Avg('communication'),
        average_quality=Avg('quality'),
        average_timeliness=Avg('timeliness')
    )
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    context = {
        'reviewed_user': user,
        'reviews': reviews,
        'stats': stats,
        'rating_distribution': rating_distribution,
    }
    return render(request, 'reviews/user_reviews.html', context)

@login_required
def respond_to_review(request, review_id):
    """Respond to a review (only by the reviewee)"""
    review = get_object_or_404(Review, id=review_id, reviewee=request.user)
    
    # Check if response already exists
    if hasattr(review, 'response'):
        messages.info(request, 'You have already responded to this review.')
        return redirect('reviews:user_reviews', user_id=request.user.id)
    
    if request.method == 'POST':
        form = ReviewResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.save()
            
            messages.success(request, 'Response posted successfully!')
            return redirect('reviews:user_reviews', user_id=request.user.id)
    else:
        form = ReviewResponseForm()
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'reviews/respond_to_review.html', context)

class MyReviewsView(LoginRequiredMixin, ListView):
    template_name = 'reviews/my_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user).select_related('reviewee').order_by('-created_at')

def update_user_rating(user):
    """Update user's overall rating based on reviews"""
    reviews = Review.objects.filter(reviewee=user)
    if reviews.exists():
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        
        # Update freelancer profile if exists
        if hasattr(user, 'freelancer_profile'):
            user.freelancer_profile.success_rate = (avg_rating / 5) * 100
            user.freelancer_profile.save()