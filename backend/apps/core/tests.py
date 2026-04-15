"""Tests for auth flow: register, login, refresh."""
from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import User


class AuthFlowTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_register(self) -> None:
        resp = self.client.post(
            "/api/auth/register/",
            {"email": "new@example.com", "password": "super-secret-1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_login_and_refresh(self) -> None:
        User.objects.create_user(email="user@example.com", password="pass-longer-1")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "user@example.com", "password": "pass-longer-1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        refresh = data["refresh"]
        resp2 = self.client.post(
            "/api/auth/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertIn("access", resp2.json())

    def test_me_requires_auth(self) -> None:
        resp = self.client.get("/api/me/")
        self.assertEqual(resp.status_code, 401)
