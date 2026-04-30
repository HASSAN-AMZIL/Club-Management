from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ClubForm
from .models import Club


@login_required
def dashboard_view(request):
    return render(request, 'clubs/dashboard.html')


@login_required
def my_club_view(request):
    club = Club.objects.order_by('id').first()
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
