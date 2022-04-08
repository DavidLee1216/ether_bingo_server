from django.test import TestCase
from os import listdir
from os.path import join, isdir


class TestClass(TestCase):
    def test_urls(self):
        GAME_APP_DIR = 'game'

        GAME_DIRS = ['bingo']
        entities = [GAME_DIR+'.'+directory for GAME_DIR in GAME_DIRS
                    for directory in listdir(join(GAME_APP_DIR, GAME_DIR))
                    if (isdir(join(GAME_APP_DIR, GAME_DIR, directory))
                        and directory != '__pycache__')]
        print(entities)
        urlpatterns = [
            'game.{}.urls'.format(entity)
            for entity in entities
        ]

        print(urlpatterns)
