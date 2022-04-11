from dataclasses import field, fields
from rest_framework import serializers
from .models import BingoGame, BingoBids, BingoGameStatus


class BingoGameStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoGameStatus
        fields = '__all__'


class BingoGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoGame
        fields = '__all__'


class BingoBidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoBids
        fields = '__all__'
