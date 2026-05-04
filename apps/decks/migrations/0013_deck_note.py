import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0012_alter_deck_crm_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeckNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('kind', models.CharField(max_length=20, choices=[
                    ('general', 'General Note'),
                    ('mis', 'MIS / Financials'),
                    ('whatsapp', 'WhatsApp / Chat'),
                    ('call', 'Call Note'),
                ], default='general')),
                ('title', models.CharField(max_length=255, blank=True)),
                ('body', models.TextField()),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='decks.deck')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
