# Initial migration for the Deck model.

import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('startup_name', models.CharField(max_length=255)),
                ('original_filename', models.CharField(max_length=255)),
                ('s3_pdf_key', models.CharField(blank=True, max_length=500)),
                ('openai_file_id', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(
                    choices=[('uploaded', 'Uploaded'), ('processing', 'Processing'), ('complete', 'Complete'), ('failed', 'Failed')],
                    default='uploaded', max_length=20,
                )),
                ('business_model', models.TextField(blank=True)),
                ('industry_context', models.TextField(blank=True)),
                ('key_risks', models.JSONField(default=list)),
                ('founder_questions', models.JSONField(default=list)),
                ('error_message', models.TextField(blank=True)),
                ('uploaded_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
