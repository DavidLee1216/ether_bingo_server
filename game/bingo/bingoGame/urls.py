from . import views
from rest_framework import routers
from django.urls import path, include, re_path
from ether_bingo_server.settings import BASE_DIR
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('bingo_bid/', views.bid, name='bingo_bid'),
]
