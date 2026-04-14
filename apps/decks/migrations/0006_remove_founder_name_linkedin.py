# Migration: removes founder_name and founder_linkedin, keeps only founder_email.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0005_founder_contact'),
    ]

    operations = [
        migrations.RemoveField(model_name='deck', name='founder_name'),
        migrations.RemoveField(model_name='deck', name='founder_linkedin'),
    ]
