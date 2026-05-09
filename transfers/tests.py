from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, League
from players.models import Player, Stats
from .models import Transfer


class TransferListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scout', password='password123')
        self.premier_league = League.objects.get(name='Premier League', country='England')
        self.la_liga = League.objects.get(name='La Liga', country='Spain')

        self.my_club = Club.objects.create(
            name='Atlas United',
            league=self.premier_league,
            founded_year=1998,
            country='England',
            city='Manchester',
            stadium='Atlas Arena',
            coach='Youssef Amrani',
            budget=8500000,
            logo_url='Atlas United.png',
            trophies_count=7,
        )
        self.external_club = Club.objects.create(
            name='Madrid Stars',
            league=self.la_liga,
            founded_year=1902,
            country='Spain',
            city='Madrid',
            stadium='Madrid Arena',
            coach='Carlo Blanco',
            budget=250000000,
            logo_url='Madrid Stars.png',
            trophies_count=35,
        )
        self.other_external_club = Club.objects.create(
            name='Sevilla Town',
            league=self.la_liga,
            founded_year=1905,
            country='Spain',
            city='Sevilla',
            stadium='Town Park',
            coach='Luis Vega',
            budget=60000000,
            logo_url='Sevilla Town.png',
            trophies_count=5,
        )

        self.my_player = self.create_player('Home Striker', self.my_club, 'ST', 81)
        self.external_player = self.create_player('Target Midfielder', self.external_club, 'CM', 88)
        self.other_external_player = self.create_player('Wide Runner', self.other_external_club, 'LW', 77)
        self.transfer = Transfer.objects.create(
            player=self.external_player,
            from_club=self.external_club,
            to_club=self.my_club,
            price=12000000,
            date=date(2026, 4, 12),
        )

    def create_player(self, name, club, position, overall):
        player = Player.objects.create(
            name=name,
            age=24,
            position=position,
            value=2300000,
            join_date=date(2024, 7, 12),
            image_url=f'{name}.png',
            club=club,
        )
        Stats.objects.create(
            player=player,
            overall=overall,
            form=Stats.FORM_GOOD,
            pace=84,
            shooting=82,
            passing=79,
            defense=58,
            dribbling=81,
        )
        return player

    def test_transfer_list_requires_login(self):
        response = self.client.get(reverse('transfer_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_transfer_list_excludes_my_club_players(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.my_player.name)
        self.assertContains(response, self.external_player.name)
        self.assertContains(response, self.other_external_player.name)

    def test_transfer_list_shows_expected_columns_and_links(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_list'))

        self.assertContains(response, 'Target Midfielder')
        self.assertContains(response, '24')
        self.assertContains(response, 'CM')
        self.assertContains(response, '88')
        self.assertContains(response, '2300000')
        self.assertContains(response, 'Madrid Stars')
        self.assertContains(response, reverse('transfer_player_detail', args=[self.external_player.id]))
        self.assertContains(response, reverse('transfer_club_detail', args=[self.external_club.id]))
        self.assertContains(response, reverse('transfer_history'))

    def test_transfer_search_matches_player_name_only(self):
        self.client.login(username='scout', password='password123')

        name_response = self.client.get(reverse('transfer_list'), {'q': 'Target'})
        team_response = self.client.get(reverse('transfer_list'), {'q': 'Sevilla'})

        self.assertContains(name_response, self.external_player.name)
        self.assertNotContains(name_response, self.other_external_player.name)
        self.assertNotContains(team_response, self.other_external_player.name)
        self.assertNotContains(team_response, self.external_player.name)

    def test_transfer_position_filter_matches_position_option(self):
        self.client.login(username='scout', password='password123')

        position_response = self.client.get(reverse('transfer_list'), {'position': 'CM'})

        self.assertContains(position_response, self.external_player.name)
        self.assertNotContains(position_response, self.other_external_player.name)

    def test_transfer_search_and_position_filter_can_combine(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_list'), {'q': 'Target', 'position': 'LW'})

        self.assertContains(response, 'No players match your search.')
        self.assertNotContains(response, self.external_player.name)
        self.assertNotContains(response, self.other_external_player.name)

    def test_read_only_player_detail_hides_mutating_actions(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_player_detail', args=[self.external_player.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.external_player.name)
        self.assertContains(response, 'Back to Transfers')
        self.assertContains(response, 'Generate Report')
        self.assertContains(response, reverse('transfer_player_generate_report', args=[self.external_player.id]))
        self.assertNotContains(response, 'Download PDF Report')
        self.assertNotContains(response, 'Edit Player')
        self.assertNotContains(response, 'Delete Player')

    def test_read_only_player_detail_can_generate_report(self):
        self.client.login(username='scout', password='password123')
        report = 'Balanced midfielder with good technical quality.'
        url = reverse('transfer_player_generate_report', args=[self.external_player.id])

        with patch('transfers.views.generate_scouting_report', return_value=report) as generate_report:
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        generate_report.assert_called_once()
        self.assertContains(response, 'Scouting Report')
        self.assertContains(response, report)
        self.assertContains(response, 'Back to Transfers')
        self.assertNotContains(response, 'Download PDF Report')
        self.assertNotContains(response, 'Edit Player')
        self.assertNotContains(response, 'Delete Player')

    def test_read_only_club_detail_hides_my_club_actions(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_club_detail', args=[self.external_club.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.external_club.name)
        self.assertContains(response, 'Back to Transfers')
        self.assertNotContains(response, 'View Players')
        self.assertNotContains(response, 'Edit Club')

    def test_transfer_history_requires_login(self):
        response = self.client.get(reverse('transfer_history'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_transfer_history_is_read_only(self):
        self.client.login(username='scout', password='password123')

        response = self.client.get(reverse('transfer_history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Transfer History')
        self.assertContains(response, self.external_player.name)
        self.assertContains(response, self.external_club.name)
        self.assertContains(response, self.my_club.name)
        self.assertContains(response, '12000000')
        self.assertContains(response, 'April 12, 2026')
        self.assertContains(response, 'Back to Transfers')
        self.assertNotContains(response, 'Edit')
        self.assertNotContains(response, 'Delete')
