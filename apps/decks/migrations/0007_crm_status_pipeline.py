# Migration: expands crm_status choices to full pipeline statuses and increases max_length.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0006_remove_founder_name_linkedin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='crm_status',
            field=models.CharField(
                max_length=30,
                default='pending',
                choices=[
                    ('pending', 'Pending'),
                    ('portfolio', 'Portfolio Company'),
                    ('active', 'Active'),
                    ('decision_needed', 'Decision To Be Taken'),
                    ('dm_call', 'DM Call Setup / TBD'),
                    ('deep_dive', 'Need To Deep Dive'),
                    ('update_requested', 'Update Requested / Founder Followed Up'),
                    ('intro_call_done', 'Introductory Call Done'),
                    ('wait_watch', 'Wait and Watch'),
                    ('tracking', 'Tracking'),
                    ('not_raising', 'Not Raising, Introductory Call Done'),
                    ('will_raise', 'Will Raise Soon'),
                    ('early_undecided', 'Early, Undecided'),
                    ('connected_tbd', 'Connected, Calls To Be Decided'),
                    ('unresponsive', 'Founder Unresponsive'),
                    ('not_fit', 'Not a Fit'),
                    ('evaluated_pass', 'Evaluated, Pass'),
                    ('pass', 'Pass'),
                ],
            ),
        ),
    ]
