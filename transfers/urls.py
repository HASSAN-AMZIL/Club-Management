from django.urls import path

from . import views

urlpatterns = [
    path('transfers/', views.transfer_list_view, name='transfer_list'),
    path('transfers/players/<int:player_id>/', views.transfer_player_detail_view, name='transfer_player_detail'),
    path('transfers/clubs/<int:club_id>/', views.transfer_club_detail_view, name='transfer_club_detail'),
]
