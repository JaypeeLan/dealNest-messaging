from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    notification_delay_minutes = models.IntegerField(
        default=1,
        help_text="Minutes to wait before sending unread message notification"
    )
    
    def __str__(self):
        return f"{self.username} ({self.email})"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_task_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"
    
    def get_unread_count_for_recipient(self):
        return Message.objects.filter(recipient=self.recipient, is_read=False).count()
