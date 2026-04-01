# Serializer for FirmPreferences — exposes all editable fields for GET and PUT.

from rest_framework import serializers
from .models import FirmPreferences


class FirmPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmPreferences
        fields = ['sectors_focus', 'stage_focus', 'question_style', 'additional_context', 'updated_at']
        read_only_fields = ['updated_at']
