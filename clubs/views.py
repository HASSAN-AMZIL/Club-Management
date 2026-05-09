from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import ClubForm
from .models import Club, Match
from players.models import Player, Stats
from players.utils import format_money
from transfers.models import Transfer


POSITION_GROUPS = [
    ('Attack', ['ST', 'CF', 'LW', 'RW'], '#84CC16'),
    ('Center', ['CDM', 'CM', 'CAM', 'LM', 'RM'], '#22C55E'),
    ('Defence', ['CB', 'LB', 'RB', 'LWB', 'RWB'], '#38BDF8'),
    ('GK', ['GK'], '#F59E0B'),
]


@login_required
def dashboard_view(request):
    club = Club.objects.select_related('league').order_by('id').first()

    if club is None:
        return redirect('my_club')

    players = Player.objects.filter(club=club).select_related('stats')
    aggregates = players.aggregate(
        total_value=Sum('value'),
        avg_age=Avg('age'),
    )
    player_count = players.count()
    top_player = players.order_by('-stats__overall', '-value', 'name').first()
    recent_transfers = (
        Transfer.objects.filter(Q(from_club=club) | Q(to_club=club))
        .select_related('player', 'from_club', 'to_club')
        .order_by('-date', 'player__name')[:5]
    )
    position_chart_items = [
        {
            'label': label,
            'count': players.filter(position__in=positions).count(),
            'color': color,
        }
        for label, positions, color in POSITION_GROUPS
    ]

    return render(
        request,
        'clubs/dashboard.html',
        {
            'club': club,
            'player_count': player_count,
            'squad_value': format_money(aggregates['total_value']),
            'avg_age': round(aggregates['avg_age'] or 0),
            'recent_transfers': recent_transfers,
            'top_player': top_player,
            'older_players_count': players.filter(age__gt=30).count(),
            'underperforming_count': players.filter(stats__form=Stats.FORM_BAD).count(),
            'position_chart_items': position_chart_items,
            'position_chart': {
                'labels': [item['label'] for item in position_chart_items],
                'counts': [item['count'] for item in position_chart_items],
                'colors': [item['color'] for item in position_chart_items],
            },
        },
    )


@login_required
def my_club_view(request):
    club = Club.objects.select_related('league').order_by('id').first()
    edit_mode = request.method == 'POST' or request.GET.get('edit') == '1' or club is None

    if request.method == 'POST':
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            form.save()
            return redirect('my_club')
    else:
        form = ClubForm(instance=club)

    return render(
        request,
        'clubs/my_club.html',
        {
            'club': club,
            'edit_mode': edit_mode,
            'form': form,
        },
    )


@login_required
def matches_view(request):
    club = Club.objects.select_related('league').order_by('id').first()

    if club is None:
        return redirect('my_club')

    today = timezone.localdate()
    my_matches = Match.objects.filter(Q(club1=club) | Q(club2=club)).select_related('club1', 'club2')
    match_history = my_matches.filter(date__lt=today).order_by('-date')
    next_matches = my_matches.filter(date__gte=today).order_by('date')

    return render(
        request,
        'clubs/matches.html',
        {
            'club': club,
            'match_history': match_history,
            'next_matches': next_matches,
        },
    )
