from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    
    author_name = serializers.SerializerMethodField()

    def get_author_name(self, obj):
        return obj.author.username if obj.author else None

    class Meta:
        model = CustomUser
        fields = ['id', 'custom', 'address', 'phone']