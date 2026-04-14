# Migration: adds sector, crm_status fields to Deck model.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0003_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='sector',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='deck',
            name='crm_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                max_length=20,
            ),
        ),
    ]
