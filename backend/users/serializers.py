# users/serializers.py
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "second_last_name",
            "phone_number",
            "birth_date",
            "dni",
            "neighborhood",
            "address",
            "city",
            "role",
            "date_joined",
            "is_active",
            "license_number",
        ]
        read_only_fields = ["id", "date_joined"]


class InspectorSerializer(serializers.ModelSerializer):
    """Serializer for Inspector users"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "second_last_name",
            "full_name",
            "phone_number",
        ]
