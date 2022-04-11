from dataclasses import field
from rest_framework import serializers
from .models import UserProfile, UserCoin, UserCoinBuyHistory


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
