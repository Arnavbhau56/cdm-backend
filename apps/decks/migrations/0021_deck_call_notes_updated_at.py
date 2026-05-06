from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0020_merge_0018_update_user_prompt_0019_update_user_prompt'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='call_notes_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
