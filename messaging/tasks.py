from celery import current_app
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@current_app.task(bind=True)
def send_unread_notification(self, message_id):
    """Send unread message notification if message is still unread"""
    from .models import Message
    
    try:
        message = Message.objects.get(id=message_id)
        
        if message.is_read:
            logger.info(f"Message {message_id} was read, skipping notification")
            return f"Message {message_id} was read, notification cancelled"
        
        unread_count = message.get_unread_count_for_recipient()
        
        subject = "You have unread messages"
        body = f"You have {unread_count} unread message{'s' if unread_count != 1 else ''}. Visit /messages to read them."
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.recipient.email],
            fail_silently=False,
        )
        
        logger.info(f"Unread notification sent to {message.recipient.email} for message {message_id}")
        return f"Notification sent to {message.recipient.email}"
        
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
        return f"Message {message_id} not found"
    except Exception as e:
        logger.error(f"Error sending notification for message {message_id}: {str(e)}")
        raise
