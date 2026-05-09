from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from clubs.models import Club, League, Match
from players.models import Player, Stats
from transfers.models import Transfer


class Command(BaseCommand):
    help = 'Load presentation-ready football scouting demo data.'

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

        self.stdout.write(self.style.SUCCESS('Presentation demo data loaded successfully.'))

    def create_leagues(self):
        leagues_data = [
            ('Premier League', 'England'),
            ('La Liga', 'Spain'),
            ('Serie A', 'Italy'),
            ('Bundesliga', 'Germany'),
            ('Ligue 1', 'France'),
        ]

        leagues = {}
        for name, country in leagues_data:
            league, _ = League.objects.update_or_create(
                name=name,
                country=country,
                defaults={'name': name, 'country': country},
            )
            leagues[name] = league

        return leagues

    def create_clubs(self, leagues):
        clubs_data = [
            {
                'name': 'Real Madrid',
                'league': leagues['La Liga'],
                'founded_year': 1902,
                'country': 'Spain',
                'city': 'Madrid',
                'stadium': 'Santiago Bernabeu',
                'coach': 'Alvaro Arbeloa',
                'budget': 240000000,
                'logo_url': 'Real Madrid.png',
                'trophies_count': 105,
            },
            {
                'name': 'Manchester City',
                'league': leagues['Premier League'],
                'founded_year': 1880,
                'country': 'England',
                'city': 'Manchester',
                'stadium': 'Etihad Stadium',
                'coach': 'Pep Guardiola',
                'budget': 210000000,
                'logo_url': 'Manchester City.png',
                'trophies_count': 36,
            },
            {
                'name': 'FC Barcelona',
                'league': leagues['La Liga'],
                'founded_year': 1899,
                'country': 'Spain',
                'city': 'Barcelona',
                'stadium': 'Camp Nou',
                'coach': 'Hansi Flick',
                'budget': 160000000,
                'logo_url': 'FC Barcelona.png',
                'trophies_count': 99,
            },
            {
                'name': 'Bayern Munich',
                'league': leagues['Bundesliga'],
                'founded_year': 1900,
                'country': 'Germany',
                'city': 'Munich',
                'stadium': 'Allianz Arena',
                'coach': 'Vincent Kompany',
                'budget': 175000000,
                'logo_url': 'Bayern Munich.png',
                'trophies_count': 84,
            },
            {
                'name': 'Paris Saint-Germain',
                'league': leagues['Ligue 1'],
                'founded_year': 1970,
                'country': 'France',
                'city': 'Paris',
                'stadium': 'Parc des Princes',
                'coach': 'Luis Enrique',
                'budget': 190000000,
                'logo_url': 'Paris Saint-Germain.png',
                'trophies_count': 52,
            },
            {
                'name': 'Inter Milan',
                'league': leagues['Serie A'],
                'founded_year': 1908,
                'country': 'Italy',
                'city': 'Milan',
                'stadium': 'San Siro',
                'coach': 'Simone Inzaghi',
                'budget': 130000000,
                'logo_url': 'Inter Milan.png',
                'trophies_count': 46,
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
            # Real Madrid, the presentation "my club".
            self.player('Thibaut Courtois', 34, 'GK', 28000000, 2018, 'Real Madrid', 89, Stats.FORM_GOOD, 52, 38, 72, 88, 58),
            self.player('Andriy Lunin', 27, 'GK', 18000000, 2018, 'Real Madrid', 81, Stats.FORM_AVERAGE, 48, 32, 67, 80, 51),
            self.player('Dani Carvajal', 34, 'RB', 10000000, 2013, 'Real Madrid', 82, Stats.FORM_AVERAGE, 72, 62, 77, 82, 77),
            self.player('Trent Alexander-Arnold', 27, 'RB', 75000000, 2025, 'Real Madrid', 86, Stats.FORM_GOOD, 78, 74, 92, 78, 84),
            self.player('Eder Militao', 28, 'CB', 60000000, 2019, 'Real Madrid', 85, Stats.FORM_GOOD, 83, 48, 72, 87, 74),
            self.player('Antonio Rudiger', 33, 'CB', 25000000, 2022, 'Real Madrid', 86, Stats.FORM_AVERAGE, 78, 48, 70, 89, 67),
            self.player('David Alaba', 33, 'CB', 14000000, 2021, 'Real Madrid', 82, Stats.FORM_BAD, 70, 68, 82, 81, 78),
            self.player('Alvaro Carreras', 23, 'LB', 50000000, 2025, 'Real Madrid', 81, Stats.FORM_GOOD, 84, 52, 76, 80, 82),
            self.player('Dean Huijsen', 21, 'CB', 65000000, 2025, 'Real Madrid', 82, Stats.FORM_GOOD, 76, 45, 78, 84, 76),
            self.player('Aurelien Tchouameni', 26, 'CDM', 85000000, 2022, 'Real Madrid', 86, Stats.FORM_GOOD, 72, 70, 84, 86, 81),
            self.player('Eduardo Camavinga', 23, 'CM', 90000000, 2021, 'Real Madrid', 85, Stats.FORM_GOOD, 82, 70, 84, 82, 87),
            self.player('Federico Valverde', 27, 'CM', 115000000, 2018, 'Real Madrid', 88, Stats.FORM_GOOD, 88, 80, 86, 82, 86),
            self.player('Jude Bellingham', 22, 'CAM', 180000000, 2023, 'Real Madrid', 90, Stats.FORM_GOOD, 82, 84, 88, 79, 90),
            self.player('Arda Guler', 21, 'CAM', 55000000, 2023, 'Real Madrid', 81, Stats.FORM_GOOD, 75, 78, 84, 48, 86),
            self.player('Brahim Diaz', 26, 'RW', 40000000, 2023, 'Real Madrid', 82, Stats.FORM_AVERAGE, 83, 78, 80, 44, 86),
            self.player('Franco Mastantuono', 18, 'RW', 45000000, 2025, 'Real Madrid', 78, Stats.FORM_AVERAGE, 78, 75, 79, 42, 83),
            self.player('Rodrygo', 25, 'RW', 100000000, 2019, 'Real Madrid', 86, Stats.FORM_AVERAGE, 88, 82, 82, 45, 90),
            self.player('Vinicius Junior', 25, 'LW', 150000000, 2018, 'Real Madrid', 89, Stats.FORM_GOOD, 95, 83, 82, 38, 94),
            self.player('Kylian Mbappe', 27, 'ST', 180000000, 2024, 'Real Madrid', 91, Stats.FORM_GOOD, 97, 88, 84, 42, 93),

            # Manchester City.
            self.player('Gianluigi Donnarumma', 27, 'GK', 40000000, 2025, 'Manchester City', 87, Stats.FORM_GOOD, 55, 32, 76, 86, 58),
            self.player('Rodri', 29, 'CDM', 130000000, 2019, 'Manchester City', 89, Stats.FORM_GOOD, 66, 80, 90, 87, 84),
            self.player('Tijjani Reijnders', 27, 'CM', 65000000, 2025, 'Manchester City', 84, Stats.FORM_GOOD, 78, 80, 86, 74, 84),
            self.player('Phil Foden', 25, 'RW', 140000000, 2017, 'Manchester City', 87, Stats.FORM_GOOD, 82, 84, 86, 58, 89),
            self.player('Erling Haaland', 25, 'ST', 180000000, 2022, 'Manchester City', 91, Stats.FORM_GOOD, 89, 94, 66, 45, 80),

            # FC Barcelona.
            self.player('Joan Garcia', 25, 'GK', 25000000, 2025, 'FC Barcelona', 82, Stats.FORM_GOOD, 58, 30, 74, 82, 58),
            self.player('Pau Cubarsi', 19, 'CB', 70000000, 2024, 'FC Barcelona', 82, Stats.FORM_GOOD, 73, 39, 77, 84, 74),
            self.player('Pedri', 23, 'CM', 120000000, 2020, 'FC Barcelona', 87, Stats.FORM_GOOD, 78, 78, 90, 70, 91),
            self.player('Lamine Yamal', 18, 'RW', 180000000, 2023, 'FC Barcelona', 86, Stats.FORM_GOOD, 88, 82, 84, 38, 91),
            self.player('Marcus Rashford', 28, 'LW', 45000000, 2025, 'FC Barcelona', 82, Stats.FORM_AVERAGE, 90, 82, 78, 42, 84),

            # Bayern Munich.
            self.player('Manuel Neuer', 39, 'GK', 5000000, 2011, 'Bayern Munich', 84, Stats.FORM_AVERAGE, 52, 33, 80, 83, 56),
            self.player('Dayot Upamecano', 27, 'CB', 50000000, 2021, 'Bayern Munich', 84, Stats.FORM_GOOD, 82, 45, 73, 86, 73),
            self.player('Jamal Musiala', 23, 'CAM', 140000000, 2020, 'Bayern Munich', 88, Stats.FORM_GOOD, 86, 84, 86, 62, 93),
            self.player('Michael Olise', 24, 'RW', 70000000, 2024, 'Bayern Munich', 84, Stats.FORM_GOOD, 84, 81, 85, 49, 88),
            self.player('Harry Kane', 32, 'ST', 90000000, 2023, 'Bayern Munich', 90, Stats.FORM_GOOD, 70, 93, 86, 50, 83),

            # Paris Saint-Germain.
            self.player('Achraf Hakimi', 27, 'RB', 65000000, 2021, 'Paris Saint-Germain', 85, Stats.FORM_GOOD, 91, 72, 82, 81, 85),
            self.player('Nuno Mendes', 23, 'LB', 75000000, 2022, 'Paris Saint-Germain', 84, Stats.FORM_GOOD, 92, 64, 78, 82, 86),
            self.player('Vitinha', 26, 'CM', 80000000, 2022, 'Paris Saint-Germain', 86, Stats.FORM_GOOD, 78, 78, 90, 74, 88),
            self.player('Ousmane Dembele', 28, 'RW', 90000000, 2023, 'Paris Saint-Germain', 87, Stats.FORM_GOOD, 93, 86, 84, 42, 92),
            self.player('Khvicha Kvaratskhelia', 25, 'LW', 85000000, 2025, 'Paris Saint-Germain', 86, Stats.FORM_GOOD, 86, 83, 82, 44, 91),

            # Inter Milan.
            self.player('Yann Sommer', 37, 'GK', 4000000, 2023, 'Inter Milan', 83, Stats.FORM_AVERAGE, 50, 30, 72, 82, 55),
            self.player('Alessandro Bastoni', 27, 'CB', 70000000, 2017, 'Inter Milan', 86, Stats.FORM_GOOD, 74, 58, 82, 88, 77),
            self.player('Nicolo Barella', 29, 'CM', 75000000, 2020, 'Inter Milan', 86, Stats.FORM_GOOD, 82, 78, 87, 82, 86),
            self.player('Hakan Calhanoglu', 32, 'CDM', 35000000, 2021, 'Inter Milan', 84, Stats.FORM_AVERAGE, 68, 82, 88, 76, 82),
            self.player('Lautaro Martinez', 28, 'ST', 110000000, 2018, 'Inter Milan', 89, Stats.FORM_GOOD, 82, 90, 80, 54, 87),
        ]

        players = {}
        for data in players_data:
            stats_data = data.pop('stats')
            player, _ = Player.objects.update_or_create(
                name=data['name'],
                club=data['club'],
                defaults=data,
            )
            Stats.objects.update_or_create(
                player=player,
                defaults=stats_data,
            )
            players[player.name] = player

        return players

    def player(self, name, age, position, value, join_year, club_name, overall, form, pace, shooting, passing, defense, dribbling):
        return {
            'name': name,
            'age': age,
            'position': position,
            'value': value,
            'join_date': date(join_year, 7, 1),
            'image_url': f'{name}.png',
            'club': Club.objects.get(name=club_name),
            'stats': {
                'overall': overall,
                'form': form,
                'pace': pace,
                'shooting': shooting,
                'passing': passing,
                'defense': defense,
                'dribbling': dribbling,
            },
        }

    def create_matches(self, clubs):
        matches_data = [
            (clubs['Real Madrid'], clubs['Manchester City'], 3, 2, date(2026, 2, 18)),
            (clubs['FC Barcelona'], clubs['Real Madrid'], 1, 2, date(2026, 3, 8)),
            (clubs['Real Madrid'], clubs['Inter Milan'], 2, 0, date(2026, 4, 14)),
            (clubs['Bayern Munich'], clubs['Real Madrid'], None, None, date(2026, 5, 22)),
            (clubs['Real Madrid'], clubs['Paris Saint-Germain'], None, None, date(2026, 6, 4)),
            (clubs['Real Madrid'], clubs['FC Barcelona'], None, None, date(2026, 6, 21)),
            (clubs['Manchester City'], clubs['Bayern Munich'], 2, 2, date(2026, 3, 20)),
            (clubs['Paris Saint-Germain'], clubs['Inter Milan'], 1, 1, date(2026, 4, 28)),
        ]

        for club1, club2, score1, score2, match_date in matches_data:
            Match.objects.update_or_create(
                club1=club1,
                club2=club2,
                date=match_date,
                defaults={
                    'club1_score': score1,
                    'club2_score': score2,
                },
            )

    def create_transfers(self, clubs, players):
        transfers_data = [
            (players['Kylian Mbappe'], clubs['Paris Saint-Germain'], clubs['Real Madrid'], 0, date(2024, 7, 1)),
            (players['Jude Bellingham'], clubs['Borussia Dortmund'] if 'Borussia Dortmund' in clubs else clubs['Bayern Munich'], clubs['Real Madrid'], 103000000, date(2023, 7, 1)),
            (players['Trent Alexander-Arnold'], clubs['Manchester City'], clubs['Real Madrid'], 75000000, date(2025, 7, 1)),
            (players['Harry Kane'], clubs['Manchester City'], clubs['Bayern Munich'], 95000000, date(2023, 7, 1)),
            (players['Ousmane Dembele'], clubs['FC Barcelona'], clubs['Paris Saint-Germain'], 50000000, date(2023, 8, 12)),
        ]

        for player, from_club, to_club, price, transfer_date in transfers_data:
            Transfer.objects.update_or_create(
                player=player,
                from_club=from_club,
                to_club=to_club,
                date=transfer_date,
                defaults={'price': price},
            )
