from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0015_industry_context_jsonfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='insight',
            field=models.JSONField(default=dict),
        ),
    ]
