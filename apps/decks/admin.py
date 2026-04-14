# Django admin registration for Deck and Comment with import/export support via django-import-export.

from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Deck, Comment


class DeckResource(resources.ModelResource):
    class Meta:
        model = Deck
        fields = (
            'id', 'startup_name', 'sector', 'original_filename',
            'status', 'crm_status', 'business_model', 'industry_context',
            'pdf_url', 'created_at', 'updated_at',
        )
        export_order = fields


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'body', 'created_at']


@admin.register(Deck)
class DeckAdmin(ImportExportModelAdmin):
    resource_class = DeckResource
    list_display = ['startup_name', 'sector', 'founder_email', 'status', 'crm_status', 'uploaded_by', 'created_at']
    list_filter = ['crm_status', 'status', 'sector']
    search_fields = ['startup_name', 'sector', 'founder_email']
    readonly_fields = ['id', 'openai_file_id', 'pdf_url', 'created_at', 'updated_at']
    list_editable = ['crm_status']
    inlines = [CommentInline]


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = ('id', 'deck__startup_name', 'author__username', 'body', 'created_at')


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource
    list_display = ['deck', 'author', 'body', 'created_at']
    search_fields = ['deck__startup_name', 'body']
