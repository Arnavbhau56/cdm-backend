# Migration: converts founder_questions from list of strings to list of {question, answer} objects.
# Existing string entries are migrated to {question: str, answer: ""}.

from django.db import migrations


def migrate_questions(apps, schema_editor):
    Deck = apps.get_model('decks', 'Deck')
    for deck in Deck.objects.all():
        if not deck.founder_questions:
            continue
        converted = []
        for item in deck.founder_questions:
            if isinstance(item, str):
                converted.append({'question': item, 'answer': ''})
            elif isinstance(item, dict):
                converted.append({'question': item.get('question', ''), 'answer': item.get('answer', '')})
        deck.founder_questions = converted
        deck.save(update_fields=['founder_questions'])


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0007_crm_status_pipeline'),
    ]

    operations = [
        migrations.RunPython(migrate_questions, reverse_code=migrations.RunPython.noop),
    ]
