from rest_framework import serializers
from .models import Notification, NotificationRecipient


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True, default=None)
    sender_role = serializers.CharField(source='sender.role', read_only=True, default=None)
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at', 'sender_name', 'sender_role', 'is_read', 'read_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        try:
            recipient = obj.recipients.get(user=request.user)
            return recipient.is_read
        except NotificationRecipient.DoesNotExist:
            return False

    def get_read_at(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        try:
            recipient = obj.recipients.get(user=request.user)
            return recipient.read_at
        except NotificationRecipient.DoesNotExist:
            return None
