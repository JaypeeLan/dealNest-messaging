from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from celery import current_app
from datetime import timedelta
from django.utils import timezone

from .models import Message, User
from .serializers import MessageSerializer, CreateMessageSerializer, MarkReadSerializer
from .tasks import send_unread_notification

@api_view(['POST'])
def create_message(request):
    """Create a new message and schedule unread notification"""
    serializer = CreateMessageSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        sender = User.objects.get(id=data['sender_id'])
        recipient = User.objects.get(id=data['recipient_id'])
        
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            body=data['body']
        )
        
        # Schedule notification task
        delay_minutes = recipient.notification_delay_minutes
        eta = timezone.now() + timedelta(minutes=delay_minutes)
        
        task = send_unread_notification.apply_async(
            args=[message.id],
            eta=eta
        )
        
        message.notification_task_id = task.id
        message.save()
        
        response_serializer = MessageSerializer(message)
        return Response({
            'message': response_serializer.data,
            'notification_scheduled_for': eta.isoformat(),
            'task_id': task.id
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def mark_message_read(request):
    """Mark message as read and cancel pending notification"""
    serializer = MarkReadSerializer(data=request.data)
    if serializer.is_valid():
        message_id = serializer.validated_data['message_id']
        message = get_object_or_404(Message, id=message_id)
        
        message.is_read = True
        
        if message.notification_task_id:
            try:
                current_app.control.revoke(message.notification_task_id, terminate=True)
                task_cancelled = True
            except Exception as e:
                task_cancelled = False
                print(f"Could not cancel task {message.notification_task_id}: {e}")
        else:
            task_cancelled = False
        
        message.save()
        
        response_serializer = MessageSerializer(message)
        return Response({
            'message': response_serializer.data,
            'notification_cancelled': task_cancelled
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_messages(request):
    """List all messages (for testing purposes)"""
    messages = Message.objects.all()
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)
