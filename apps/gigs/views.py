from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import Gig, GigCategory, GigOrder, GigDelivery, GigFavorite
from .forms import GigForm, GigOrderForm, GigDeliveryForm

class GigListView(ListView):
    model = Gig
    template_name = 'gigs/gig_list.html'
    context_object_name = 'gigs'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Gig.objects.filter(is_active=True).select_related('freelancer', 'category').prefetch_related('images')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(skills__name__icontains=search)
            ).distinct()
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by price range
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(basic_price__gte=price_min)
        if price_max:
            queryset = queryset.filter(basic_price__lte=price_max)
        
        # Filter by delivery time
        delivery_time = self.request.GET.get('delivery_time')
        if delivery_time:
            queryset = queryset.filter(basic_delivery_time__lte=delivery_time)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'price_low':
            queryset = queryset.order_by('basic_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-basic_price')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-orders_completed')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GigCategory.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context

class GigDetailView(DetailView):
    model = Gig
    template_name = 'gigs/gig_detail.html'
    context_object_name = 'gig'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gig = self.get_object()
        
        # Increment view count
        gig.views += 1
        gig.save(update_fields=['views'])
        
        # Check if user has favorited this gig
        if self.request.user.is_authenticated:
            context['is_favorited'] = GigFavorite.objects.filter(
                user=self.request.user, gig=gig
            ).exists()
        
        # Get reviews for this gig
        from apps.reviews.models import Review
        context['reviews'] = Review.objects.filter(gig=gig).select_related('reviewer').order_by('-created_at')[:5]
        
        return context

class GigCreateView(LoginRequiredMixin, CreateView):
    model = Gig
    form_class = GigForm
    template_name = 'gigs/gig_create.html'
    success_url = reverse_lazy('gigs:my_gigs')
    
    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        return super().form_valid(form)

@login_required
def my_gigs(request):
    gigs = Gig.objects.filter(freelancer=request.user).annotate(
        total_orders=Count('orders')
    ).order_by('-created_at')
    
    return render(request, 'gigs/my_gigs.html', {'gigs': gigs})

@login_required
def order_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, is_active=True)
    
    if request.method == 'POST':
        form = GigOrderForm(request.POST, gig=gig)
        if form.is_valid():
            order = form.save(commit=False)
            order.gig = gig
            order.buyer = request.user
            
            # Calculate price based on package
            package = form.cleaned_data['package']
            if package == 'basic':
                order.price = gig.basic_price
                delivery_days = gig.basic_delivery_time
            elif package == 'standard' and gig.standard_price:
                order.price = gig.standard_price
                delivery_days = gig.standard_delivery_time
            elif package == 'premium' and gig.premium_price:
                order.price = gig.premium_price
                delivery_days = gig.premium_delivery_time
            else:
                order.price = gig.basic_price
                delivery_days = gig.basic_delivery_time
            
            # Calculate delivery date
            order.delivery_date = timezone.now() + timedelta(days=delivery_days)
            
            # Add fast delivery if selected
            if form.cleaned_data.get('fast_delivery') and gig.extra_fast_delivery:
                order.fast_delivery = True
                order.extra_price = gig.extra_fast_price or 0
                order.delivery_date = timezone.now() + timedelta(days=1)
            
            order.save()
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('gigs:order_detail', order_id=order.id)
    else:
        form = GigOrderForm(gig=gig)
    
    return render(request, 'gigs/order_gig.html', {
        'form': form,
        'gig': gig
    })

@login_required
def toggle_favorite(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    favorite, created = GigFavorite.objects.get_or_create(user=request.user, gig=gig)
    
    if not created:
        favorite.delete()
        messages.success(request, 'Gig removed from favorites.')
    else:
        messages.success(request, 'Gig added to favorites.')
    
    return redirect('gigs:gig_detail', pk=gig_id)

@login_required
def my_orders(request):
    # Orders placed by user
    bought_orders = GigOrder.objects.filter(buyer=request.user).select_related('gig').order_by('-created_at')
    
    # Orders for user's gigs
    received_orders = GigOrder.objects.filter(gig__freelancer=request.user).select_related('gig', 'buyer').order_by('-created_at')
    
    context = {
        'bought_orders': bought_orders,
        'received_orders': received_orders,
    }
    return render(request, 'gigs/my_orders.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(GigOrder, id=order_id)
    
    # Check if user is involved in this order
    if request.user != order.buyer and request.user != order.gig.freelancer:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('gigs:gig_list')
    
    return render(request, 'gigs/order_detail.html', {'order': order})

@login_required
def deliver_order(request, order_id):
    order = get_object_or_404(GigOrder, id=order_id, gig__freelancer=request.user)
    
    if order.status != 'in_progress':
        messages.error(request, 'This order cannot be delivered at this time.')
        return redirect('gigs:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = GigDeliveryForm(request.POST, request.FILES)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.order = order
            delivery.save()
            
            order.status = 'delivered'
            order.actual_delivery_date = timezone.now()
            order.save()
            
            messages.success(request, 'Order delivered successfully!')
            return redirect('gigs:order_detail', order_id=order_id)
    else:
        form = GigDeliveryForm()
    
    return render(request, 'gigs/deliver_order.html', {
        'form': form,
        'order': order
    })