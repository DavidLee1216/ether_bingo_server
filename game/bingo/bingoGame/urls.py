from . import views
from rest_framework import routers
from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('bingo_buy_ticket/', views.buy_ticket, name='bingo_buy_ticket'),
    path('get_bingo_games_info/', views.get_bingo_games_info,
         name='get_bingo_games_info'),
    path('get_bingo_game_info/', views.get_bingo_game_info,
         name='get_bingo_game_info'),
    path('get_bingo_game_general_info/', views.get_bingo_game_general_info,
         name='get_bingo_game_general_info'),
    path('get_bingo_tickets/', views.get_bingo_tickets, name='get_bingo_tickets'),
    path('get_my_bingo_tickets/', views.get_my_bingo_tickets,
         name='get_my_bingo_tickets'),

]
