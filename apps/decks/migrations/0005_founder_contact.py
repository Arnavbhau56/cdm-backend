# Migration: adds founder contact fields and emailed_questions tracking to Deck model.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0004_crm_fields'),
    ]

    operations = [
        migrations.AddField(model_name='deck', name='founder_name', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='deck', name='founder_email', field=models.EmailField(blank=True)),
        migrations.AddField(model_name='deck', name='founder_linkedin', field=models.URLField(blank=True, max_length=500)),
        migrations.AddField(model_name='deck', name='emailed_questions', field=models.JSONField(default=list)),
    ]
