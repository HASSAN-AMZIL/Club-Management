from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from clubs.models import Club, Match
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

        clubs = self.create_clubs()
        players = self.create_players(clubs)
        self.create_matches(clubs)
        self.create_transfers(clubs, players)

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully.'))

    def create_clubs(self):
        clubs_data = [
            {
                'name': 'Atlas United',
                'founded_year': 1998,
                'country': 'Morocco',
                'city': 'Casablanca',
                'stadium': 'Atlas Arena',
                'coach': 'Youssef Amrani',
                'budget': 8500000,
                'logo_url': 'https://placehold.co/300x300?text=Atlas+United',
                'trophies_count': 7,
            },
            {
                'name': 'Rabat Lions',
                'founded_year': 1985,
                'country': 'Morocco',
                'city': 'Rabat',
                'stadium': 'Capital Stadium',
                'coach': 'Karim Bennis',
                'budget': 6200000,
                'logo_url': 'https://placehold.co/300x300?text=Rabat+Lions',
                'trophies_count': 4,
            },
            {
                'name': 'Marrakech Stars',
                'founded_year': 2004,
                'country': 'Morocco',
                'city': 'Marrakech',
                'stadium': 'Palm Stadium',
                'coach': 'Nabil Haddad',
                'budget': 4800000,
                'logo_url': 'https://placehold.co/300x300?text=Marrakech+Stars',
                'trophies_count': 2,
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
                'name': 'Amine El Fassi',
                'age': 24,
                'position': 'ST',
                'value': 2300000,
                'join_date': date(2024, 7, 12),
                'image_url': 'https://placehold.co/300x300?text=Amine',
                'club': clubs['Atlas United'],
                'stats': {'pace': 84, 'shooting': 82, 'passing': 69, 'defense': 38, 'dribbling': 81},
            },
            {
                'name': 'Omar Naciri',
                'age': 21,
                'position': 'LW',
                'value': 1800000,
                'join_date': date(2025, 1, 8),
                'image_url': 'https://placehold.co/300x300?text=Omar',
                'club': clubs['Atlas United'],
                'stats': {'pace': 89, 'shooting': 74, 'passing': 72, 'defense': 35, 'dribbling': 86},
            },
            {
                'name': 'Yassine Idrissi',
                'age': 27,
                'position': 'CM',
                'value': 1500000,
                'join_date': date(2023, 8, 20),
                'image_url': 'https://placehold.co/300x300?text=Yassine',
                'club': clubs['Atlas United'],
                'stats': {'pace': 70, 'shooting': 66, 'passing': 84, 'defense': 71, 'dribbling': 78},
            },
            {
                'name': 'Mehdi Bakkali',
                'age': 29,
                'position': 'CB',
                'value': 1200000,
                'join_date': date(2022, 6, 30),
                'image_url': 'https://placehold.co/300x300?text=Mehdi',
                'club': clubs['Atlas United'],
                'stats': {'pace': 62, 'shooting': 41, 'passing': 65, 'defense': 86, 'dribbling': 58},
            },
            {
                'name': 'Bilal Haddou',
                'age': 26,
                'position': 'GK',
                'value': 950000,
                'join_date': date(2021, 9, 1),
                'image_url': 'https://placehold.co/300x300?text=Bilal',
                'club': clubs['Atlas United'],
                'stats': {'pace': 48, 'shooting': 22, 'passing': 55, 'defense': 80, 'dribbling': 43},
            },
            {
                'name': 'Samir Rahimi',
                'age': 23,
                'position': 'CAM',
                'value': 2100000,
                'join_date': date(2024, 2, 15),
                'image_url': 'https://placehold.co/300x300?text=Samir',
                'club': clubs['Rabat Lions'],
                'stats': {'pace': 78, 'shooting': 76, 'passing': 85, 'defense': 44, 'dribbling': 88},
            },
            {
                'name': 'Ayoub Tazi',
                'age': 22,
                'position': 'RB',
                'value': 1300000,
                'join_date': date(2023, 7, 18),
                'image_url': 'https://placehold.co/300x300?text=Ayoub',
                'club': clubs['Rabat Lions'],
                'stats': {'pace': 83, 'shooting': 45, 'passing': 70, 'defense': 79, 'dribbling': 72},
            },
            {
                'name': 'Reda Mansouri',
                'age': 25,
                'position': 'CDM',
                'value': 1600000,
                'join_date': date(2022, 8, 5),
                'image_url': 'https://placehold.co/300x300?text=Reda',
                'club': clubs['Marrakech Stars'],
                'stats': {'pace': 68, 'shooting': 58, 'passing': 76, 'defense': 83, 'dribbling': 70},
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
                'club1': clubs['Atlas United'],
                'club2': clubs['Rabat Lions'],
                'club1_score': 2,
                'club2_score': 1,
                'date': date(2026, 3, 12),
            },
            {
                'club1': clubs['Marrakech Stars'],
                'club2': clubs['Atlas United'],
                'club1_score': 0,
                'club2_score': 3,
                'date': date(2026, 3, 26),
            },
            {
                'club1': clubs['Rabat Lions'],
                'club2': clubs['Marrakech Stars'],
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
                'player': players['Omar Naciri'],
                'from_club': clubs['Marrakech Stars'],
                'to_club': clubs['Atlas United'],
                'price': 1800000,
                'date': date(2025, 1, 8),
            },
            {
                'player': players['Yassine Idrissi'],
                'from_club': clubs['Rabat Lions'],
                'to_club': clubs['Atlas United'],
                'price': 1500000,
                'date': date(2023, 8, 20),
            },
            {
                'player': players['Samir Rahimi'],
                'from_club': clubs['Atlas United'],
                'to_club': clubs['Rabat Lions'],
                'price': 2100000,
                'date': date(2024, 2, 15),
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
