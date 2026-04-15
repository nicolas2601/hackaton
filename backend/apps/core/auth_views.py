"""Auth-related views: register and me endpoints."""
from __future__ import annotations

from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.fincas.models import Finca
from apps.fincas.serializers import FincaSerializer

from .models import User
from .serializers import UserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user self-registration."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone"]

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ to create a new user."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    serializer_class = RegisterSerializer


class MeView(generics.RetrieveAPIView):
    """GET /api/me/ returns current user profile + owned fincas."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        data = self.get_serializer(user).data
        fincas = Finca.objects.filter(propietario=user)
        data["fincas"] = FincaSerializer(
            fincas, many=True, context={"request": request}
        ).data
        return Response(data)
