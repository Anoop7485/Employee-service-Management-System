from rest_framework import serializers
from .models import ServiceRequest

class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceRequest
        fields='__all__'
        read_only_fields=[
            'status',
            'created_at',
            'updated_at',
            'resolved_at',
            'closed_at'
        ]