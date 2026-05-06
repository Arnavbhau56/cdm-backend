from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0017_deck_website_email_text'),
    ]

    operations = [
        migrations.RemoveField(model_name='deck', name='founder_email'),
        migrations.AddField(
            model_name='deck',
            name='founder_email_1',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='deck',
            name='founder_email_2',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='deck',
            name='founder_email_3',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
