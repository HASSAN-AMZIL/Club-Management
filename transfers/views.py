from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from clubs.models import Club
from players.models import Player


def get_my_club():
    return Club.objects.select_related('league').order_by('id').first()


@login_required
def transfer_list_view(request):
    club = get_my_club()

    if club is None:
        return redirect('my_club')

    query = request.GET.get('q', '').strip()
    players = (
        Player.objects.exclude(club=club)
        .select_related('club', 'club__league', 'stats')
        .order_by('name')
    )

    if query:
        players = players.filter(
            Q(name__icontains=query)
            | Q(position__icontains=query)
            | Q(club__name__icontains=query)
        )

    return render(
        request,
        'transfers/transfer_list.html',
        {
            'club': club,
            'players': players,
            'query': query,
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
