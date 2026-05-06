from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0016_deck_insight'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='website',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='deck',
            name='founder_email',
            field=models.TextField(blank=True),
        ),
    ]
