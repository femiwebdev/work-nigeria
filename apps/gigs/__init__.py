from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Skill

User = get_user_model()

class GigCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Gig Categories"

class Gig(models.Model):
    PACKAGE_TYPES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gigs')
    category = models.ForeignKey(GigCategory, on_delete=models.CASCADE, related_name='gigs')
    skills = models.ManyToManyField(Skill, blank=True)
    
    # Basic Package
    basic_price = models.DecimalField(max_digits=10, decimal_places=2)
    basic_description = models.TextField()
    basic_delivery_time = models.PositiveIntegerField(help_text="Delivery time in days")
    basic_revisions = models.PositiveIntegerField(default=1)
    
    # Standard Package (optional)
    standard_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    standard_description = models.TextField(blank=True)
    standard_delivery_time = models.PositiveIntegerField(null=True, blank=True)
    standard_revisions = models.PositiveIntegerField(null=True, blank=True)
    
    # Premium Package (optional)
    premium_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    premium_description = models.TextField(blank=True)
    premium_delivery_time = models.PositiveIntegerField(null=True, blank=True)
    premium_revisions = models.PositiveIntegerField(null=True, blank=True)
    
    # Gig extras
    extra_fast_delivery = models.BooleanField(default=False)
    extra_fast_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Status and metrics
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    orders_completed = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_starting_price(self):
        return self.basic_price

class GigImage(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gig_images/')
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.gig.title} - Image"

class GigOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    )
    
    PACKAGE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gig_orders')
    package = models.CharField(max_length=10, choices=PACKAGE_CHOICES, default='basic')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    requirements = models.TextField(help_text="Buyer's specific requirements")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_date = models.DateTimeField()
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Extras
    fast_delivery = models.BooleanField(default=False)
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.gig.title}"
    
    @property
    def total_price(self):
        return self.price + self.extra_price

class GigDelivery(models.Model):
    order = models.OneToOneField(GigOrder, on_delete=models.CASCADE, related_name='delivery')
    message = models.TextField()
    files = models.FileField(upload_to='gig_deliveries/', blank=True, null=True)
    delivered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery for Order #{self.order.id}"

class GigRevision(models.Model):
    order = models.ForeignKey(GigOrder, on_delete=models.CASCADE, related_name='revisions')
    message = models.TextField()
    files = models.FileField(upload_to='gig_revisions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Revision for Order #{self.order.id}"

class GigFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_gigs')
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'gig')
    
    def __str__(self):
        return f"{self.user.username} - {self.gig.title}"