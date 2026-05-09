from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Club, League, Match
from players.models import Player, Stats
from transfers.models import Transfer


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scout', password='password123')
        self.league = League.objects.get(name='Premier League', country='England')
        self.my_club = self.create_club('Atlas United', trophies_count=12)
        self.other_club = self.create_club('Rival City')

    def create_club(self, name, trophies_count=7):
        return Club.objects.create(
            name=name,
            league=self.league,
            founded_year=1998,
            country='England',
            city='Manchester',
            stadium=f'{name} Stadium',
            coach='Youssef Amrani',
            budget=8500000,
            logo_url=f'{name}.png',
            trophies_count=trophies_count,
        )

    def create_player(self, name, club, age, value, overall, form=Stats.FORM_GOOD, position='CM'):
        player = Player.objects.create(
            name=name,
            age=age,
            position=position,
            value=value,
            join_date=timezone.localdate(),
            image_url=f'{name}.png',
            club=club,
        )
        Stats.objects.create(
            player=player,
            overall=overall,
            form=form,
            pace=80,
            shooting=80,
            passing=80,
            defense=80,
            dribbling=80,
        )
        return player

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_dashboard_shows_club_metrics_and_alerts(self):
        self.create_player('Veteran One', self.my_club, 35, 100000000, 85, Stats.FORM_BAD)
        self.create_player('Veteran Two', self.my_club, 36, 90000000, 88)
        self.create_player('Veteran Three', self.my_club, 37, 80000000, 82, Stats.FORM_BAD)
        self.create_player('Young Star', self.my_club, 20, 40000000, 91)
        self.create_player('Other Player', self.other_club, 24, 999000000, 99, Stats.FORM_BAD)
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Atlas United')
        self.assertContains(response, 'Players')
        self.assertContains(response, '4')
        self.assertContains(response, '€310 000 000')
        self.assertContains(response, 'Avg Age')
        self.assertContains(response, '32')
        self.assertContains(response, '12')
        self.assertContains(response, 'Young Star')
        self.assertContains(response, 'Overall 91')
        self.assertContains(response, '3 players are older than 30')
        self.assertContains(response, '2 players underperforming')
        self.assertNotContains(response, 'Other Player')

    def test_dashboard_shows_recent_transfers_involving_my_club_only(self):
        player = self.create_player('Transfer Target', self.other_club, 27, 50000000, 84)
        other_player = self.create_player('Unrelated Transfer', self.other_club, 28, 60000000, 83)
        third_club = self.create_club('Third Club')
        Transfer.objects.create(
            player=player,
            from_club=self.other_club,
            to_club=self.my_club,
            price=12000000,
            date=timezone.localdate(),
        )
        Transfer.objects.create(
            player=other_player,
            from_club=self.other_club,
            to_club=third_club,
            price=9000000,
            date=timezone.localdate(),
        )
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Recent Transfers')
        self.assertContains(response, 'Transfer Target')
        self.assertNotContains(response, 'Unrelated Transfer')

    def test_dashboard_shows_position_donut_chart_groups(self):
        self.create_player('Striker', self.my_club, 24, 10000000, 82, position='ST')
        self.create_player('Winger', self.my_club, 23, 11000000, 83, position='LW')
        self.create_player('Midfielder', self.my_club, 25, 12000000, 84, position='CM')
        self.create_player('Defender', self.my_club, 27, 9000000, 80, position='CB')
        self.create_player('Keeper', self.my_club, 29, 7000000, 79, position='GK')
        self.create_player('Other Striker', self.other_club, 24, 10000000, 82, position='ST')
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Squad Positions')
        self.assertContains(response, 'positionDonutChart')
        self.assertContains(response, 'https://cdn.jsdelivr.net/npm/chart.js')
        self.assertEqual(
            response.context['position_chart'],
            {
                'labels': ['Attack', 'Center', 'Defence', 'GK'],
                'counts': [2, 1, 1, 1],
                'colors': ['#84CC16', '#22C55E', '#38BDF8', '#F59E0B'],
            },
        )


class MatchesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scout', password='password123')
        self.league = League.objects.get(name='Premier League', country='England')
        self.my_club = self.create_club('Atlas United')
        self.rival = self.create_club('Rival City')
        self.other_club = self.create_club('Other Club')
        self.unrelated_club = self.create_club('Unrelated FC')
        self.today = timezone.localdate()

    def create_club(self, name):
        return Club.objects.create(
            name=name,
            league=self.league,
            founded_year=1998,
            country='England',
            city='Manchester',
            stadium=f'{name} Stadium',
            coach='Youssef Amrani',
            budget=8500000,
            logo_url=f'{name}.png',
            trophies_count=7,
        )

    def test_matches_requires_login(self):
        response = self.client.get(reverse('matches'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_matches_shows_only_my_club_matches(self):
        my_match = Match.objects.create(
            club1=self.my_club,
            club2=self.rival,
            club1_score=2,
            club2_score=1,
            date=self.today - timedelta(days=7),
        )
        Match.objects.create(
            club1=self.other_club,
            club2=self.unrelated_club,
            club1_score=3,
            club2_score=0,
            date=self.today - timedelta(days=4),
        )
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('matches'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_match.club2.name)
        self.assertNotContains(response, self.unrelated_club.name)

    def test_matches_split_history_and_next_matches(self):
        past_match = Match.objects.create(
            club1=self.my_club,
            club2=self.rival,
            club1_score=2,
            club2_score=1,
            date=self.today - timedelta(days=7),
        )
        today_match = Match.objects.create(
            club1=self.other_club,
            club2=self.my_club,
            club1_score=None,
            club2_score=None,
            date=self.today,
        )
        future_match = Match.objects.create(
            club1=self.my_club,
            club2=self.unrelated_club,
            club1_score=None,
            club2_score=None,
            date=self.today + timedelta(days=14),
        )
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('matches'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Match History')
        self.assertContains(response, 'Next Matches')
        self.assertContains(response, '2 - 1')
        self.assertContains(response, today_match.club1.name)
        self.assertContains(response, future_match.club2.name)
        self.assertContains(response, 'match-score">-</span>', count=2)

    def test_matches_empty_states(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('matches'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No match history available.')
        self.assertContains(response, 'No upcoming matches available.')
