# FirmPreferences model: single-row table storing CDM Capital's investment focus and question style.
# A data migration ensures one default row always exists after first migration.

from django.db import models


class FirmPreferences(models.Model):
    sectors_focus = models.TextField(blank=True)
    stage_focus = models.CharField(max_length=100, blank=True)
    question_style = models.TextField(blank=True)
    additional_context = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Firm Preferences'

    def __str__(self):
        return 'CDM Capital Preferences'
