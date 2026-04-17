# Migration: adds call_notes JSONField to Deck for manual call note sections.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0008_questions_with_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='call_notes',
            field=models.JSONField(default=dict),
        ),
    ]
