from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from clubs.models import Club, League, Match
from players.models import Player, Stats
from transfers.models import Transfer


class Command(BaseCommand):
    help = 'Load demo football scouting data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing clubs, players, matches, and transfers before loading demo data.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            Transfer.objects.all().delete()
            Match.objects.all().delete()
            Player.objects.all().delete()
            Club.objects.all().delete()

        leagues = self.create_leagues()
        clubs = self.create_clubs(leagues)
        players = self.create_players(clubs)
        self.create_matches(clubs)
        self.create_transfers(clubs, players)

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully.'))

    def create_leagues(self):
        leagues_data = [
            {'name': 'Premier League', 'country': 'England'},
            {'name': 'La Liga', 'country': 'Spain'},
            {'name': 'Serie A', 'country': 'Italy'},
            {'name': 'Bundesliga', 'country': 'Germany'},
            {'name': 'Ligue 1', 'country': 'France'},
        ]

        leagues = {}
        for data in leagues_data:
            league, _ = League.objects.update_or_create(
                name=data['name'],
                country=data['country'],
                defaults=data,
            )
            leagues[league.name] = league

        return leagues

    def create_clubs(self, leagues):
        clubs_data = [
            {
                'name': 'Manchester City',
                'league': leagues['Premier League'],
                'founded_year': 1880,
                'country': 'England',
                'city': 'Manchester',
                'stadium': 'Etihad Stadium',
                'coach': 'Pep Guardiola',
                'budget': 250000000,
                'logo_url': 'Manchester City.png',
                'trophies_count': 36,
            },
            {
                'name': 'Real Madrid',
                'league': leagues['La Liga'],
                'founded_year': 1902,
                'country': 'Spain',
                'city': 'Madrid',
                'stadium': 'Santiago Bernabeu',
                'coach': 'Xabi Alonso',
                'budget': 260000000,
                'logo_url': 'Real Madrid.png',
                'trophies_count': 105,
            },
            {
                'name': 'Borussia Dortmund',
                'league': leagues['Bundesliga'],
                'founded_year': 1909,
                'country': 'Germany',
                'city': 'Dortmund',
                'stadium': 'Signal Iduna Park',
                'coach': 'Niko Kovac',
                'budget': 150000000,
                'logo_url': 'Borussia Dortmund.png',
                'trophies_count': 22,
            },
        ]

        clubs = {}
        for data in clubs_data:
            club, _ = Club.objects.update_or_create(
                name=data['name'],
                defaults=data,
            )
            clubs[club.name] = club

        return clubs

    def create_players(self, clubs):
        players_data = [
            {
                'name': 'Erling Haaland',
                'age': 25,
                'position': 'ST',
                'value': 180000000,
                'join_date': date(2022, 7, 1),
                'image_url': 'Erling Haaland.png',
                'club': clubs['Manchester City'],
                'stats': {
                    'overall': 91,
                    'form': Stats.FORM_GOOD,
                    'pace': 89,
                    'shooting': 94,
                    'passing': 66,
                    'defense': 45,
                    'dribbling': 80,
                },
            },
            {
                'name': 'Phil Foden',
                'age': 25,
                'position': 'RW',
                'value': 140000000,
                'join_date': date(2017, 7, 1),
                'image_url': 'Phil Foden.png',
                'club': clubs['Manchester City'],
                'stats': {
                    'overall': 87,
                    'form': Stats.FORM_GOOD,
                    'pace': 82,
                    'shooting': 84,
                    'passing': 86,
                    'defense': 58,
                    'dribbling': 89,
                },
            },
            {
                'name': 'Rodri',
                'age': 29,
                'position': 'CDM',
                'value': 130000000,
                'join_date': date(2019, 7, 4),
                'image_url': 'Rodri.png',
                'club': clubs['Manchester City'],
                'stats': {
                    'overall': 89,
                    'form': Stats.FORM_AVERAGE,
                    'pace': 66,
                    'shooting': 80,
                    'passing': 90,
                    'defense': 87,
                    'dribbling': 84,
                },
            },
            {
                'name': 'Ruben Dias',
                'age': 28,
                'position': 'CB',
                'value': 80000000,
                'join_date': date(2020, 9, 29),
                'image_url': 'Ruben Dias.png',
                'club': clubs['Manchester City'],
                'stats': {
                    'overall': 86,
                    'form': Stats.FORM_AVERAGE,
                    'pace': 67,
                    'shooting': 38,
                    'passing': 77,
                    'defense': 89,
                    'dribbling': 69,
                },
            },
            {
                'name': 'Jeremy Doku',
                'age': 23,
                'position': 'LW',
                'value': 65000000,
                'join_date': date(2023, 8, 24),
                'image_url': 'Jeremy Doku.png',
                'club': clubs['Manchester City'],
                'stats': {
                    'overall': 82,
                    'form': Stats.FORM_GOOD,
                    'pace': 91,
                    'shooting': 75,
                    'passing': 77,
                    'defense': 39,
                    'dribbling': 90,
                },
            },
            {
                'name': 'Jude Bellingham',
                'age': 22,
                'position': 'CAM',
                'value': 180000000,
                'join_date': date(2023, 7, 1),
                'image_url': 'Jude Bellingham.png',
                'club': clubs['Real Madrid'],
                'stats': {
                    'overall': 90,
                    'form': Stats.FORM_GOOD,
                    'pace': 80,
                    'shooting': 86,
                    'passing': 87,
                    'defense': 78,
                    'dribbling': 88,
                },
            },
            {
                'name': 'Vinicius Junior',
                'age': 25,
                'position': 'LW',
                'value': 150000000,
                'join_date': date(2018, 7, 12),
                'image_url': 'Vinicius Junior.png',
                'club': clubs['Real Madrid'],
                'stats': {
                    'overall': 89,
                    'form': Stats.FORM_GOOD,
                    'pace': 95,
                    'shooting': 85,
                    'passing': 81,
                    'defense': 36,
                    'dribbling': 93,
                },
            },
            {
                'name': 'Brahim Diaz',
                'age': 26,
                'position': 'RW',
                'value': 40000000,
                'join_date': date(2019, 1, 6),
                'image_url': 'Brahim Diaz.png',
                'club': clubs['Real Madrid'],
                'stats': {
                    'overall': 82,
                    'form': Stats.FORM_AVERAGE,
                    'pace': 82,
                    'shooting': 79,
                    'passing': 81,
                    'defense': 43,
                    'dribbling': 86,
                },
            },
        ]

        players = {}
        for data in players_data:
            stats_data = data.pop('stats')
            player, _ = Player.objects.update_or_create(
                name=data['name'],
                defaults=data,
            )
            Stats.objects.update_or_create(
                player=player,
                defaults=stats_data,
            )
            players[player.name] = player

        return players

    def create_matches(self, clubs):
        matches_data = [
            {
                'club1': clubs['Manchester City'],
                'club2': clubs['Real Madrid'],
                'club1_score': 2,
                'club2_score': 1,
                'date': date(2026, 3, 12),
            },
            {
                'club1': clubs['Borussia Dortmund'],
                'club2': clubs['Manchester City'],
                'club1_score': 1,
                'club2_score': 3,
                'date': date(2026, 3, 26),
            },
            {
                'club1': clubs['Real Madrid'],
                'club2': clubs['Borussia Dortmund'],
                'club1_score': 1,
                'club2_score': 1,
                'date': date(2026, 4, 9),
            },
        ]

        for data in matches_data:
            Match.objects.update_or_create(
                club1=data['club1'],
                club2=data['club2'],
                date=data['date'],
                defaults={
                    'club1_score': data['club1_score'],
                    'club2_score': data['club2_score'],
                },
            )

    def create_transfers(self, clubs, players):
        transfers_data = [
            {
                'player': players['Erling Haaland'],
                'from_club': clubs['Borussia Dortmund'],
                'to_club': clubs['Manchester City'],
                'price': 60000000,
                'date': date(2022, 7, 1),
            },
            {
                'player': players['Jude Bellingham'],
                'from_club': clubs['Borussia Dortmund'],
                'to_club': clubs['Real Madrid'],
                'price': 103000000,
                'date': date(2023, 7, 1),
            },
            {
                'player': players['Brahim Diaz'],
                'from_club': clubs['Manchester City'],
                'to_club': clubs['Real Madrid'],
                'price': 17000000,
                'date': date(2019, 1, 6),
            },
        ]

        for data in transfers_data:
            Transfer.objects.update_or_create(
                player=data['player'],
                from_club=data['from_club'],
                to_club=data['to_club'],
                date=data['date'],
                defaults={'price': data['price']},
            )
