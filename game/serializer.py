from dataclasses import field
from rest_framework import serializers
from .models import HistoryKind, UserProfile, UserCoin, UserCoinBuyHistory, UserCoinConsumeHistory


class HistoryKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryKind
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCoin
        fields = ['user', 'coin']


class UserCoinBuyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCoinBuyHistory
        fields = '__all__'


class UserCoinConsumeHistory(serializers.ModelSerializer):
    class Meta:
        model = UserCoinConsumeHistory
        fields = '__all__'
