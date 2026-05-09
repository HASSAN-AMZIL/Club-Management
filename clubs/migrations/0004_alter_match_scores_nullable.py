from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0003_league_club_league'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='club1_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='club2_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
