from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    
    # Related order/project
    gig_order = models.OneToOneField('gigs.GigOrder', on_delete=models.CASCADE, null=True, blank=True, related_name='review')
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='review')
    
    # Rating and feedback
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Detailed ratings
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    timeliness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewee.username} ({self.rating}★)"
    
    @property
    def average_detailed_rating(self):
        return (self.communication + self.quality + self.timeliness) / 3

class ReviewResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to review by {self.review.reviewer.username}"