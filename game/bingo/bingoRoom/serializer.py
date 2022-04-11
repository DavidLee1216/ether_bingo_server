from .models import BingoRoom, BingoRoomAuction, BingoRoomHistory, BingoRoomAuctionBidHistory
from rest_framework import serializers
from dataclasses import field, fields


class BingoRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoRoom
        fields = '__all__'


class BingoRoomHistory(serializers.ModelSerializer):
    class Meta:
        model = BingoRoomHistory
        fields = '__all__'


class BingoRoomAuction(serializers.ModelSerializer):
    class Meta:
        model = BingoRoomAuction
        fields = '__all__'


class BingoRoomAuctionBidHistory(serializers.ModelSerializer):
    class Meta:
        model = BingoRoomAuctionBidHistory
        fields = '__all__'
