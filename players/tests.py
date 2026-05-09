from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.forms import ClubForm
from clubs.models import Club, League

from .forms import StatsForm
from .models import Player, Stats
from .services import ScoutingReportError, build_scouting_report_prompt


class PlayerReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scout', password='password123')
        self.client.login(username='scout', password='password123')
        self.league = League.objects.get(name='Premier League', country='England')
        self.club = Club.objects.create(
            name='Atlas United',
            league=self.league,
            founded_year=1998,
            country='Morocco',
            city='Casablanca',
            stadium='Atlas Arena',
            coach='Youssef Amrani',
            budget=8500000,
            logo_url='https://placehold.co/300x300?text=Atlas+United',
            trophies_count=7,
        )
        self.player = Player.objects.create(
            name='Amine El Fassi',
            age=24,
            position='ST',
            value=2300000,
            join_date=date(2024, 7, 12),
            image_url='https://placehold.co/300x300?text=Amine',
            club=self.club,
        )
        self.stats = Stats.objects.create(
            player=self.player,
            overall=84,
            form=Stats.FORM_GOOD,
            pace=84,
            shooting=82,
            passing=69,
            defense=38,
            dribbling=81,
        )


class ScoutingReportPromptTests(PlayerReportTestCase):
    def test_prompt_uses_player_club_value_and_stats(self):
        prompt = build_scouting_report_prompt(self.player, self.stats)

        self.assertIn('Name: Amine El Fassi', prompt)
        self.assertIn('Age: 24', prompt)
        self.assertIn('Position: ST', prompt)
        self.assertIn('Club: Atlas United', prompt)
        self.assertIn('Price: 2300000', prompt)
        self.assertIn('- Overall: 84', prompt)
        self.assertIn('- Form: Good', prompt)
        self.assertIn('- Pace: 84', prompt)
        self.assertIn('- Shooting: 82', prompt)
        self.assertIn('- Passing: 69', prompt)
        self.assertIn('- Defense: 38', prompt)
        self.assertIn('- Dribbling: 81', prompt)


class PlayerStatsFormTests(TestCase):
    def test_stats_form_accepts_overall_and_form(self):
        form = StatsForm(
            data={
                'overall': 84,
                'form': Stats.FORM_GOOD,
                'pace': 84,
                'shooting': 82,
                'passing': 69,
                'defense': 38,
                'dribbling': 81,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        stats = form.save(commit=False)
        self.assertEqual(stats.overall, 84)
        self.assertEqual(stats.form, Stats.FORM_GOOD)


class ClubFormTests(TestCase):
    def test_club_form_requires_league(self):
        form = ClubForm(
            data={
                'name': 'Atlas United',
                'founded_year': 1998,
                'country': 'Morocco',
                'city': 'Casablanca',
                'stadium': 'Atlas Arena',
                'coach': 'Youssef Amrani',
                'budget': 8500000,
                'logo_url': 'https://placehold.co/300x300?text=Atlas+United',
                'trophies_count': 7,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('league', form.errors)


class PlayerGenerateReportViewTests(PlayerReportTestCase):
    def test_generate_report_post_shows_mocked_report(self):
        url = reverse('player_generate_report', args=[self.player.id])
        report = 'Quick forward with strong pace and shooting for Atlas United.'

        with patch('players.views.generate_scouting_report', return_value=report) as generate_report:
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        generate_report.assert_called_once()
        self.assertContains(response, 'Scouting Report')
        self.assertContains(response, report)

    def test_generate_report_post_shows_ollama_error(self):
        url = reverse('player_generate_report', args=[self.player.id])
        message = 'Ollama is not available. Please make sure it is running locally.'

        with patch(
            'players.views.generate_scouting_report',
            side_effect=ScoutingReportError(message),
        ):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, message)
        self.assertNotContains(response, 'Scouting Report')

    def test_generate_report_post_requires_stats(self):
        self.stats.delete()
        url = reverse('player_generate_report', args=[self.player.id])

        with patch('players.views.generate_scouting_report') as generate_report:
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        generate_report.assert_not_called()
        self.assertContains(
            response,
            'Player stats are required before generating a scouting report.',
        )
