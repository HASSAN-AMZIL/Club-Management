from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import ClubForm
from .models import Club, Match


@login_required
def dashboard_view(request):
    return render(request, 'clubs/dashboard.html')


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
