from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from clubs.models import Club
from players.models import Player
from players.services import ScoutingReportError, generate_scouting_report
from .models import Transfer


def get_my_club():
    return Club.objects.select_related('league').order_by('id').first()


@login_required
def transfer_list_view(request):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    query = request.GET.get('q', '').strip()
    selected_position = request.GET.get('position', '').strip()
    players = (
        Player.objects.exclude(club=club)
        .select_related('club', 'club__league', 'stats')
        .order_by('name')
    )

    if query:
        players = players.filter(name__icontains=query)

    if selected_position:
        players = players.filter(position=selected_position)

    return render(
        request,
        'transfers/transfer_list.html',
        {
            'club': club,
            'players': players,
            'query': query,
            'position_choices': Player.POSITION_CHOICES,
            'selected_position': selected_position,
        },
    )


@login_required
def transfer_history_view(request):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    transfers = (
        Transfer.objects.select_related('player', 'from_club', 'to_club')
        .order_by('-date', 'player__name')
    )

    return render(
        request,
        'transfers/transfer_history.html',
        {
            'club': club,
            'transfers': transfers,
        },
    )


@login_required
def transfer_player_detail_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(
        Player.objects.select_related('club', 'club__league', 'stats'),
        id=player_id,
    )

    if player.club_id == club.id:
        return redirect('player_detail', player_id=player.id)

    return render(
        request,
        'players/player_detail.html',
        {
            'club': club,
            'player': player,
            'read_only': True,
        },
    )


@login_required
@require_POST
def transfer_player_generate_report_view(request, player_id):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    player = get_object_or_404(
        Player.objects.select_related('club', 'club__league', 'stats'),
        id=player_id,
    )

    if player.club_id == club.id:
        return redirect('player_generate_report', player_id=player.id)

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
            'read_only': True,
            'scouting_report': report,
            'report_error': report_error,
        },
    )


@login_required
def transfer_club_detail_view(request, club_id):
    my_club = get_my_club()

    if my_club is None:
        return redirect('my_club')

    club = get_object_or_404(Club.objects.select_related('league'), id=club_id)

    if club.id == my_club.id:
        return redirect('my_club')

    return render(
        request,
        'clubs/my_club.html',
        {
            'club': club,
            'edit_mode': False,
            'read_only': True,
        },
    )
