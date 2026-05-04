from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0014_deck_registered_name_sub_sector_one_liner'),
    ]

    operations = [
        migrations.RunSQL(
            # Convert existing text rows to a JSON object with a single legacy key
            sql="""
                ALTER TABLE decks_deck
                ADD COLUMN industry_context_new jsonb DEFAULT '{}'::jsonb;

                UPDATE decks_deck
                SET industry_context_new = jsonb_build_object('legacy', industry_context)
                WHERE industry_context IS NOT NULL AND industry_context != '';

                ALTER TABLE decks_deck DROP COLUMN industry_context;
                ALTER TABLE decks_deck RENAME COLUMN industry_context_new TO industry_context;
            """,
            reverse_sql="""
                ALTER TABLE decks_deck
                ADD COLUMN industry_context_old text DEFAULT '';

                UPDATE decks_deck
                SET industry_context_old = COALESCE(industry_context->>'legacy', '');

                ALTER TABLE decks_deck DROP COLUMN industry_context;
                ALTER TABLE decks_deck RENAME COLUMN industry_context_old TO industry_context;
            """,
        ),
    ]
