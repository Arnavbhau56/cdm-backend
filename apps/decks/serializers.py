# Serializers for Deck (list + detail), founder contact update, and Comment models.

from rest_framework import serializers
from .models import Deck, Comment, DeckMaterial


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
        fields = ['id', 'startup_name', 'sector', 'status', 'crm_status', 'founder_email_1', 'created_at', 'latest_comment']

    def get_latest_comment(self, obj):
        c = obj.comments.last()
        if not c:
            return None
        return {'body': c.body, 'author_name': c.author.get_full_name() or c.author.username if c.author else 'Unknown'}


class DeckDetailSerializer(serializers.ModelSerializer):
    materials = serializers.SerializerMethodField()
    notes_list = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = [
            'id', 'startup_name', 'registered_name', 'website', 'sector', 'sub_sector', 'one_liner',
            'original_filename', 'status', 'crm_status',
            'founder_email_1', 'founder_email_2', 'founder_email_3',
            'business_model', 'industry_context', 'key_risks',
            'founder_questions', 'emailed_questions', 'call_notes', 'call_notes_updated_at', 'error_message', 'pdf_url', 'created_at',
            'materials', 'notes_list',
        ]

    def get_materials(self, obj):
        return [{'id': str(m.id), 'name': m.name, 'url': m.url, 'created_at': m.created_at.isoformat()} for m in obj.materials.all()]

    def get_notes_list(self, obj):
        return [{'id': str(n.id), 'kind': n.kind, 'title': n.title or '', 'created_at': n.created_at.isoformat()} for n in obj.notes.all()]


class FounderContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['founder_email_1', 'founder_email_2', 'founder_email_3']


class DeckMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckMaterial
        fields = ['id', 'name', 'url', 'created_at']
