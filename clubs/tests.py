from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Club, League, Match


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
