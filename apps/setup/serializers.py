# Serializer for FirmPreferences — exposes all editable fields for GET and PUT.

from rest_framework import serializers
from .models import FirmPreferences, Prompt


class FirmPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmPreferences
        fields = ['sectors_focus', 'stage_focus', 'question_style', 'additional_context', 'updated_at']
        read_only_fields = ['updated_at']


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'key', 'title', 'body', 'updated_at']
        read_only_fields = ['id', 'key', 'updated_at']
