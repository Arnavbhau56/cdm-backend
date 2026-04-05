# Serializers for Deck model: list view (summary) and detail view (full analysis fields).
# CommentSerializer handles reading and writing user comments on a deck.

from rest_framework import serializers
from .models import Deck, Comment


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


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author_name', 'created_at']
        read_only_fields = ['id', 'author_name', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username if obj.author else 'Unknown'
