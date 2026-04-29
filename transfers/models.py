from django.db import models


class Transfer(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(
        'players.Player',
        on_delete=models.CASCADE,
        related_name='transfers',
    )
    from_club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='transfers_out',
    )
    to_club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='transfers_in',
    )
    price = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f'{self.player} from {self.from_club} to {self.to_club}'
