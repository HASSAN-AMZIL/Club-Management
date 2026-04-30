from django.db import models


class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'GK'),
        ('CB', 'CB'),
        ('LB', 'LB'),
        ('RB', 'RB'),
        ('LWB', 'LWB'),
        ('RWB', 'RWB'),
        ('CDM', 'CDM'),
        ('CM', 'CM'),
        ('CAM', 'CAM'),
        ('LM', 'LM'),
        ('RM', 'RM'),
        ('LW', 'LW'),
        ('RW', 'RW'),
        ('ST', 'ST'),
        ('CF', 'CF'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    value = models.FloatField()
    join_date = models.DateField()
    image_url = models.CharField(max_length=500)
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='players',
    )

    def __str__(self):
        return f'{self.name} ({self.position})'


class Stats(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name='stats',
    )
    pace = models.IntegerField()
    shooting = models.IntegerField()
    passing = models.IntegerField()
    defense = models.IntegerField()
    dribbling = models.IntegerField()

    def __str__(self):
        return f'Stats for {self.player}'
