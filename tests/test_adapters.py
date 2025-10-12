"""Tests for custom django-allauth adapters."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from sitebuilder.adapters import AccountAdapter

User = get_user_model()


class AccountAdapterUnitTests(TestCase):
    """Unit tests for the AccountAdapter."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.adapter = AccountAdapter()

    def test_signup_is_not_open(self):
        """Test that signup is disabled."""
        request = self.factory.get("/")
        self.assertFalse(self.adapter.is_open_for_signup(request))

    def test_login_redirect_url(self):
        """Test that login redirects to profile."""
        request = self.factory.get("/")
        redirect_url = self.adapter.get_login_redirect_url(request)
        self.assertEqual(redirect_url, "/profile/")

    def test_logout_redirect_url(self):
        """Test that logout redirects to home."""
        request = self.factory.get("/")
        redirect_url = self.adapter.get_logout_redirect_url(request)
        self.assertEqual(redirect_url, "/")
