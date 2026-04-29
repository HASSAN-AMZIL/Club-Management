from django.urls import path

from . import views

urlpatterns = [
    path('my-players/', views.my_players_view, name='my_players'),
    path('my-players/add/', views.player_create_view, name='player_add'),
    path('my-players/<int:player_id>/', views.player_detail_view, name='player_detail'),
    path('my-players/<int:player_id>/generate-report/', views.player_generate_report_view, name='player_generate_report'),
    path('my-players/<int:player_id>/edit/', views.player_update_view, name='player_edit'),
    path('my-players/<int:player_id>/delete/', views.player_delete_view, name='player_delete'),
]
