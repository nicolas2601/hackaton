"""Core app serializers for auth and user management."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Tenant, UserActivityLog


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id", "name", "slug", "nit", "address", "phone", "email",
            "is_active", "subscription_plan", "subscription_expires_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "phone", "avatar", "is_active", "role", "tenant", "tenant_name",
            "notification_preferences", "date_joined", "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email", "password", "first_name", "last_name",
            "phone", "tenant", "role",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user data."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "role": self.user.role,
            "tenant_id": str(self.user.tenant.id) if self.user.tenant else None,
        }
        return data


class UserActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserActivityLog
        fields = [
            "id", "user", "user_email", "tenant", "action", "model_type",
            "model_id", "description", "ip_address", "user_agent", "metadata",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]