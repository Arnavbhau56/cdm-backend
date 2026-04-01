# Serializers for Deck model: list view (summary) and detail view (full analysis fields).

from rest_framework import serializers
from .models import Deck


class DeckListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'startup_name', 'status', 'created_at']


class DeckDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            'id', 'startup_name', 'original_filename', 'status',
            'business_model', 'industry_context', 'key_risks',
            'founder_questions', 'error_message', 'pdf_url', 'created_at',
        ]
