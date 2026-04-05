# Deck model: stores pitch deck metadata, Cloudinary PDF URL, OpenAI reference, and all 4 AI-generated analysis fields.
# Comment model: stores user notes attached to a deck.

import uuid
from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup_name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    pdf_url = models.URLField(max_length=500, blank=True)
    openai_file_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    business_model = models.TextField(blank=True)
    industry_context = models.TextField(blank=True)
    key_risks = models.JSONField(default=list)
    founder_questions = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.startup_name


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} on {self.deck}'
