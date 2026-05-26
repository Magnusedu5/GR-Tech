from rest_framework import serializers
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    """Used for the public contact form submission."""
    class Meta:
        model  = Inquiry
        fields = ['name', 'email', 'project_type', 'message']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        return value.strip()

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Message must be at least 10 characters.')
        return value.strip()


class InquiryAdminSerializer(serializers.ModelSerializer):
    """Used for the admin dashboard — full read + status update."""
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    status_display       = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Inquiry
        fields = [
            'id', 'name', 'email', 'project_type', 'project_type_display',
            'message', 'status', 'status_display', 'ip_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'name', 'email', 'project_type', 'project_type_display',
            'message', 'ip_address', 'created_at', 'updated_at', 'status_display',
        ]
