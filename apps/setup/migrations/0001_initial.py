# Initial migration for FirmPreferences model + data migration to seed one default row.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FirmPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sectors_focus', models.TextField(blank=True)),
                ('stage_focus', models.CharField(blank=True, max_length=100)),
                ('question_style', models.TextField(blank=True)),
                ('additional_context', models.TextField(blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name_plural': 'Firm Preferences'},
        ),
        migrations.RunSQL(
            "INSERT INTO setup_firmpreferences (id, sectors_focus, stage_focus, question_style, additional_context, updated_at) "
            "VALUES (1, '', '', '', '', NOW()) ON CONFLICT DO NOTHING;",
            reverse_sql="DELETE FROM setup_firmpreferences WHERE id = 1;",
        ),
    ]
