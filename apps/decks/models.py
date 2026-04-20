# Deck and Comment models. Deck includes sector, crm_status, founder contact info, and emailed question tracking.

import uuid
from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    ANALYSIS_STATUS = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    CRM_STATUS = [
        ('pending', 'Pending'),
        ('portfolio', 'Portfolio Company'),
        ('active', 'Active'),
        ('decision_needed', 'Decision To Be Taken'),
        ('dm_call', 'DM Call Setup / TBD'),
        ('deep_dive', 'Need To Deep Dive'),
        ('update_requested', 'Update Requested / Founder Followed Up'),
        ('intro_call_done', 'Introductory Call Done'),
        ('wait_watch', 'Wait and Watch'),
        ('tracking', 'Tracking'),
        ('not_raising', 'Not Raising, Introductory Call Done'),
        ('will_raise', 'Will Raise Soon'),
        ('early_undecided', 'Early, Undecided'),
        ('connected_tbd', 'Connected, Calls To Be Decided'),
        ('unresponsive', 'Founder Unresponsive'),
        ('not_fit', 'Not a Fit'),
        ('evaluated_pass', 'Evaluated, Pass'),
        ('pass', 'Pass'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255, blank=True)
    original_filename = models.CharField(max_length=255)
    pdf_url = models.URLField(max_length=500, blank=True)
    openai_file_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS, default='uploaded')
    crm_status = models.CharField(max_length=20, choices=CRM_STATUS, default='pending')
    # Founder contact
    founder_email = models.EmailField(blank=True)
    # Analysis fields
    business_model = models.TextField(blank=True)
    industry_context = models.TextField(blank=True)
    key_risks = models.JSONField(default=list)
    founder_questions = models.JSONField(default=list)  # list of {question: str, answer: str}
    emailed_questions = models.JSONField(default=list)  # indices of questions already emailed
    call_notes = models.JSONField(default=dict)  # {overview, problem, solution, ...}
    error_message = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.startup_name


class DeckMaterial(models.Model):
    """Any additional file uploaded against a deck (pitch notes, financials, etc.)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.deck}'


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
