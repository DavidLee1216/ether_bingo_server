from . import views
from rest_framework import routers
from os import listdir
from os.path import join, isdir

from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

GAME_APP_DIR = 'game'
GAME_DIRS = ['bingo']
entities = [GAME_DIR+'.'+directory for GAME_DIR in GAME_DIRS
            for directory in listdir(join(BASE_DIR, GAME_APP_DIR, GAME_DIR))
            if (isdir(join(BASE_DIR, GAME_APP_DIR, GAME_DIR, directory))
                and directory != '__pycache__')]

urlpatterns = [
    re_path(r'^', include('game.{}.urls'.format(entity)))
    for entity in entities
]
