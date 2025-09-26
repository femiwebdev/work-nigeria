from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    subject = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Related to specific project or gig
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    gig_order = models.ForeignKey('gigs.GigOrder', on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participants_names = ", ".join([user.username for user in self.participants.all()])
        return f"Conversation: {participants_names}"
    
    def get_last_message(self):
        return self.messages.last()
    
    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."

class MessageRead(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')