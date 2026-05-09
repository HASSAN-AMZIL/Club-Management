from django.db import models


class League(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'country'],
                name='unique_league_name_country',
            ),
        ]

    def __str__(self):
        return self.name


class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    league = models.ForeignKey(
        League,
        on_delete=models.PROTECT,
        related_name='clubs',
    )
    founded_year = models.IntegerField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    stadium = models.CharField(max_length=100)
    coach = models.CharField(max_length=100)
    budget = models.FloatField()
    logo_url = models.CharField(max_length=500)
    trophies_count = models.IntegerField()

    def __str__(self):
        return self.name


class Match(models.Model):
    id = models.AutoField(primary_key=True)
    club1 = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='home_matches',
    )
    club2 = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='away_matches',
    )
    club1_score = models.IntegerField()
    club2_score = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f'{self.club1} {self.club1_score} - {self.club2_score} {self.club2}'
