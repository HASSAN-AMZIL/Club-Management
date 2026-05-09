from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from clubs.models import Club

from .forms import PlayerForm, StatsForm
from .models import Player, Stats
from .services import ScoutingReportError, generate_scouting_report


def get_my_club():
    return Club.objects.select_related('league').order_by('id').first()


@login_required
def my_players_view(request):
    club = get_my_club()
    players = Player.objects.none()

    if club is not None:
        players = (
            Player.objects.filter(club=club)
            .select_related('club')
            .select_related('stats')
            .order_by('name')
        )

    return render(
        request,
        'players/my_players.html',
        {
            'club': club,
            'players': players,
        },
    )


@login_required
def player_detail_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(
        Player.objects.select_related('club', 'stats'),
        id=player_id,
        club=club,
    )

    return render(
        request,
        'players/player_detail.html',
        {
            'club': club,
            'player': player,
        },
    )


@login_required
@require_POST
def player_generate_report_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(
        Player.objects.select_related('club', 'stats'),
        id=player_id,
        club=club,
    )
    stats = getattr(player, 'stats', None)
    report = None
    report_error = None

    if stats is None:
        report_error = 'Player stats are required before generating a scouting report.'
    else:
        try:
            report = generate_scouting_report(player, stats)
        except ScoutingReportError as exc:
            report_error = str(exc)

    return render(
        request,
        'players/player_detail.html',
        {
            'club': club,
            'player': player,
            'scouting_report': report,
            'report_error': report_error,
        },
    )


@login_required
def player_create_view(request):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    if request.method == 'POST':
        player_form = PlayerForm(request.POST)
        stats_form = StatsForm(request.POST)

        if player_form.is_valid() and stats_form.is_valid():
            with transaction.atomic():
                player = player_form.save(commit=False)
                player.club = club
                player.save()

                stats = stats_form.save(commit=False)
                stats.player = player
                stats.save()

            return redirect('my_players')
    else:
        player_form = PlayerForm()
        stats_form = StatsForm()

    return render(
        request,
        'players/player_form.html',
        {
            'club': club,
            'player_form': player_form,
            'stats_form': stats_form,
            'title': 'Add Player',
            'button_text': 'Add Player',
        },
    )


@login_required
def player_update_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(Player, id=player_id, club=club)
    stats = getattr(player, 'stats', None)

    if request.method == 'POST':
        player_form = PlayerForm(request.POST, instance=player)
        stats_form = StatsForm(request.POST, instance=stats)

        if player_form.is_valid() and stats_form.is_valid():
            with transaction.atomic():
                player = player_form.save(commit=False)
                player.club = club
                player.save()

                stats = stats_form.save(commit=False)
                stats.player = player
                stats.save()

            return redirect('my_players')
    else:
        player_form = PlayerForm(instance=player)
        stats_form = StatsForm(instance=stats)

    return render(
        request,
        'players/player_form.html',
        {
            'club': club,
            'player': player,
            'player_form': player_form,
            'stats_form': stats_form,
            'title': 'Edit Player',
            'button_text': 'Save Changes',
        },
    )


@login_required
def player_delete_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(Player, id=player_id, club=club)

    if request.method == 'POST':
        player.delete()
        return redirect('my_players')

    return render(
        request,
        'players/player_confirm_delete.html',
        {
            'club': club,
            'player': player,
        },
    )
