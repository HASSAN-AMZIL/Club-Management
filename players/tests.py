from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.forms import ClubForm
from clubs.models import Club, League

from .forms import PlayerForm, StatsForm
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
        self.assertIn('Price: €2 300 000', prompt)
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


class PlayerFormTests(TestCase):
    def test_player_form_does_not_show_image_url_field(self):
        form = PlayerForm()

        self.assertNotIn('image_url', form.fields)


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


class PlayerCreateViewTests(PlayerReportTestCase):
    def test_add_player_sets_image_url_from_player_name(self):
        response = self.client.post(
            reverse('player_add'),
            {
                'name': 'New Striker',
                'age': 22,
                'position': 'ST',
                'value': 1200000,
                'join_date': '2026-07-01',
                'overall': 78,
                'form': Stats.FORM_AVERAGE,
                'pace': 80,
                'shooting': 77,
                'passing': 65,
                'defense': 35,
                'dribbling': 76,
            },
        )

        self.assertRedirects(response, reverse('my_players'))
        player = Player.objects.get(name='New Striker')
        self.assertEqual(player.image_url, 'New Striker.png')


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
        self.assertContains(response, 'Generated with AI model')

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
        self.assertNotContains(response, 'id="reportMeta"')

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


class PlayerDownloadReportViewTests(PlayerReportTestCase):
    def test_download_report_requires_login(self):
        self.client.logout()

        response = self.client.post(reverse('player_download_report', args=[self.player.id]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_player_detail_shows_download_pdf_button(self):
        response = self.client.get(reverse('player_detail', args=[self.player.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Download PDF Report')
        self.assertContains(response, reverse('player_download_report', args=[self.player.id]))

    def test_download_report_is_limited_to_my_club_players(self):
        other_club = Club.objects.create(
            name='Rival Club',
            league=self.league,
            founded_year=2001,
            country='Morocco',
            city='Rabat',
            stadium='Rival Arena',
            coach='Rival Coach',
            budget=1200000,
            logo_url='rival.png',
            trophies_count=1,
        )
        other_player = Player.objects.create(
            name='Rival Player',
            age=26,
            position='CM',
            value=1000000,
            join_date=date(2023, 8, 1),
            image_url='rival.png',
            club=other_club,
        )

        response = self.client.post(reverse('player_download_report', args=[other_player.id]))

        self.assertEqual(response.status_code, 404)

    def test_download_report_returns_pdf_attachment(self):
        response = self.client.post(reverse('player_download_report', args=[self.player.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="player-report-amine-el-fassi.pdf"',
        )
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_download_report_includes_submitted_ai_text(self):
        report = 'Quick forward with strong pace and shooting for Atlas United.'

        with patch('players.views.generate_scouting_report') as generate_report:
            response = self.client.post(
                reverse('player_download_report', args=[self.player.id]),
                {'scouting_report': report},
            )

        self.assertEqual(response.status_code, 200)
        generate_report.assert_not_called()
        self.assertIn(b'AI Scouting Report', response.content)
        self.assertIn(report.encode('utf-8'), response.content)

    def test_download_report_omits_ai_section_without_submitted_text(self):
        response = self.client.post(reverse('player_download_report', args=[self.player.id]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'AI Scouting Report', response.content)
