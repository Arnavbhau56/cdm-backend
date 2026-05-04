from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0013_deck_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='registered_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='deck',
            name='sub_sector',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='deck',
            name='one_liner',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
