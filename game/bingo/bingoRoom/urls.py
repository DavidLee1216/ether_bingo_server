from . import views
from rest_framework import routers
from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('bingo_room_bid/', views.bid, name='bingo_room_bid'),
    path('get_room_auction_user_info/', views.get_room_auction_user_info,
         name='get_room_auction_user_info'),
    path('pay_for_winner/', views.pay_for_winner, name='pay_for_winner')
]
