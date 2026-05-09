# Generated for fixed leagues and required club league assignment.

import django.db.models.deletion
from django.db import migrations, models


LEAGUES = [
    ('Premier League', 'England'),
    ('La Liga', 'Spain'),
    ('Serie A', 'Italy'),
    ('Bundesliga', 'Germany'),
    ('Ligue 1', 'France'),
]


def seed_leagues_and_assign_clubs(apps, schema_editor):
    League = apps.get_model('clubs', 'League')
    Club = apps.get_model('clubs', 'Club')

    leagues_by_country = {}
    for name, country in LEAGUES:
        league, _ = League.objects.update_or_create(
            name=name,
            country=country,
            defaults={'name': name, 'country': country},
        )
        leagues_by_country[country] = league

    fallback_league = leagues_by_country['England']
    for club in Club.objects.all():
        club.league = leagues_by_country.get(club.country, fallback_league)
        club.save(update_fields=['league'])


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0002_alter_club_logo_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(
                        fields=('name', 'country'),
                        name='unique_league_name_country',
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name='club',
            name='league',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='clubs',
                to='clubs.league',
            ),
        ),
        migrations.RunPython(seed_leagues_and_assign_clubs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='club',
            name='league',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='clubs',
                to='clubs.league',
            ),
        ),
    ]
