from . import views
from rest_framework import routers
from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('bingo_room_bid/', views.bid, name='bingo_room_bid'),
    path('get_room_auction_user_info/', views.get_room_auction_user_info,
         name='get_room_auction_user_info'),
    path('pay_for_winner/', views.pay_for_winner, name='pay_for_winner'),
    path('assign_ownership/', views.assign_ownership, name='assign_ownership'),
    path('remove_ownership/', views.remove_ownership, name='remove_ownership'),
    path('get_room_auctions/', views.arrange_room_auctions,
         name='get_room_auctions'),
    path('get_room_setting/', views.get_room_setting, name='get_room_setting'),
    path('get_won_room_auction/', views.get_won_room_auction,
         name='get_won_room_auction'),
    path('get_own_room/', views.get_own_room, name='get_own_room'),
]
