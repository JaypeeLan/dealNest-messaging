from rest_framework import serializers
from .models import Message, User

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'body', 'is_read', 'created_at',
            'sender_username', 'recipient_username'
        ]
        read_only_fields = ['id', 'created_at', 'is_read']

class CreateMessageSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()
    body = serializers.CharField(max_length=1000)
    
    def validate_sender_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Sender does not exist")
        return value
    
    def validate_recipient_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipient does not exist")
        return value

class MarkReadSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    
    def validate_message_id(self, value):
        if not Message.objects.filter(id=value).exists():
            raise serializers.ValidationError("Message does not exist")
        return value
