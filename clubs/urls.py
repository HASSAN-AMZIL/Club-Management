from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-club/', views.my_club_view, name='my_club'),
    path('matches/', views.matches_view, name='matches'),
]
