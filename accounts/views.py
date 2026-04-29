from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        error_message = 'Invalid username or password.'

    return render(request, 'accounts/login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('login')

# Create your views here.
