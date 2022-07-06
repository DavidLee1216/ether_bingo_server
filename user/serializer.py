from django.db import models
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'last_login', 'date_joined', 'is_superuser', 'wallet_address']
        extra_kwags = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
