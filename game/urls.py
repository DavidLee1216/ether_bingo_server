from . import views
from rest_framework import routers
from os import listdir
from os.path import join, isdir

from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR

GAME_APP_DIR = 'game'
GAME_DIRS = ['bingo']
entities = [GAME_DIR+'.'+directory for GAME_DIR in GAME_DIRS
            for directory in listdir(join(BASE_DIR, GAME_APP_DIR, GAME_DIR))
            if (isdir(join(BASE_DIR, GAME_APP_DIR, GAME_DIR, directory))
                and directory != '__pycache__')]

urlpatterns = [
    re_path(r'^', include('{}.{}.urls'.format(GAME_APP_DIR, entity)))
    for entity in entities
]

urlpatterns += [
    path('profile/set/', views.set_profile, name='set_profile'),
    path('profile/<str:username>/', views.get_profile, name='get_profile'),
    path('coin/buy/', views.buy_coin, name='buy_coin')
]
