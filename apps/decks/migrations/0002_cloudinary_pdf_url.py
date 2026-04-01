# Migration: replaces s3_pdf_key CharField with pdf_url URLField for Cloudinary storage.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(model_name='deck', name='s3_pdf_key'),
        migrations.AddField(
            model_name='deck',
            name='pdf_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
