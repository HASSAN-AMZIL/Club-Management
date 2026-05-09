# Generated for player overall rating and form tracking.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_alter_player_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='overall',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stats',
            name='form',
            field=models.CharField(
                choices=[('Good', 'Good'), ('Average', 'Average'), ('Bad', 'Bad')],
                default='Average',
                max_length=7,
            ),
        ),
    ]
