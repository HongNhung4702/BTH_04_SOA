from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    userName = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['IdUser', 'UserName', 'Password', 'Token']

