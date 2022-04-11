from . import views
from rest_framework import routers
from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('bingo_buy_ticket/', views.buy_ticket, name='bingo_buy_ticket'),
    path('get_bingo_room_info/', views.get_bingo_room_info,
         name='get_bingo_room_info')

]
