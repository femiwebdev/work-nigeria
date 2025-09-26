from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from .models import Conversation, Message
from .forms import MessageForm

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Mark messages as read
    unread_messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    for message in unread_messages:
        message.is_read = True
        message.save()
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            return redirect('messaging:conversation_detail', conversation_id=conversation_id)
    else:
        form = MessageForm()
    
    messages_list = conversation.messages.select_related('sender').order_by('created_at')
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def start_conversation(request, user_id):
    """Start a new conversation with another user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).filter(
        project__isnull=True,
        gig_order__isnull=True
    ).first()
    
    if existing_conversation:
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def project_conversation(request, project_id):
    """Get or create conversation for a specific project"""
    from apps.projects.models import Project
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is involved in the project
    if request.user != project.client and request.user != project.assigned_freelancer:
        messages.error(request, 'You are not authorized to access this conversation.')
        return redirect('messaging:inbox')
    
    # Get or create conversation for this project
    conversation, created = Conversation.objects.get_or_create(
        project=project,
        defaults={'subject': f'Project: {project.title}'}
    )
    
    if created:
        # Add participants
        conversation.participants.add(project.client)
        if project.assigned_freelancer:
            conversation.participants.add(project.assigned_freelancer)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def gig_conversation(request, order_id):
    """Get or create conversation for a specific gig order"""
    from apps.gigs.models import GigOrder
    
    order = get_object_or_404(GigOrder, id=order_id)
    
    # Check if user is involved in the order
    if request.user != order.buyer and request.user != order.gig.freelancer:
        messages.error(request, 'You are not authorized to access this conversation.')
        return redirect('messaging:inbox')
    
    # Get or create conversation for this gig order
    conversation, created = Conversation.objects.get_or_create(
        gig_order=order,
        defaults={'subject': f'Gig Order: {order.gig.title}'}
    )
    
    if created:
        # Add participants
        conversation.participants.add(order.buyer, order.gig.freelancer)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@require_POST
@login_required
def send_message_ajax(request, conversation_id):
    """Send message via AJAX"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'success': False, 'error': 'Message content is required.'})
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    # Update conversation timestamp
    conversation.save()
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })