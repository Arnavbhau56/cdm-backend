# Serializers for Deck (list + detail), founder contact update, and Comment models.

from rest_framework import serializers
from .models import Deck, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author_name', 'created_at']
        read_only_fields = ['id', 'author_name', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username if obj.author else 'Unknown'


class DeckListSerializer(serializers.ModelSerializer):
    latest_comment = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ['id', 'startup_name', 'sector', 'status', 'crm_status', 'founder_email', 'created_at', 'latest_comment']

    def get_latest_comment(self, obj):
        c = obj.comments.last()
        if not c:
            return None
        return {'body': c.body, 'author_name': c.author.get_full_name() or c.author.username if c.author else 'Unknown'}


class DeckDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            'id', 'startup_name', 'sector', 'original_filename', 'status', 'crm_status',
            'founder_email',
            'business_model', 'industry_context', 'key_risks',
            'founder_questions', 'emailed_questions', 'error_message', 'pdf_url', 'created_at',
        ]


class FounderContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['founder_email']
