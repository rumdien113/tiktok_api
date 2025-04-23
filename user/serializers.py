from rest_framework import serializers
from .models import User

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstname', 'lastname',
                  'birthdate', 'phone', 'gender', 'avatar', 'bio']
        read_only_fields = ['id', 'username', 'email']
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
