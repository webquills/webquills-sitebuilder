"""Tests for views and basic functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class HomePageViewTests(TestCase):
    """Tests for the home page view."""

    def setUp(self):
        """Set up test client and user."""
        super().setUp()
        self.home_url = reverse("home")

    def test_home_page_loads_successfully(self):
        """Test that the home page loads with 200 status."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that the home page uses the correct template."""
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, "index.html")

    def test_home_page_shows_login_link_when_not_authenticated(self):
        """Test that login options are displayed for anonymous users."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Sign In")
        self.assertContains(response, "/accounts/login/")

    def test_home_page_shows_logout_when_authenticated(self):
        """Test that authenticated users see logout option."""
        # Create and login user
        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(self.home_url)
        self.assertContains(response, "Logout")
        self.assertContains(response, "/accounts/logout/")


class ProfileViewTests(TestCase):
    """Tests for the profile view."""

    def setUp(self):
        """Set up test client and user."""
        super().setUp()
        self.profile_url = reverse("profile")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_profile_redirects_when_not_authenticated(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/profile/")

    def test_profile_loads_when_authenticated(self):
        """Test that authenticated users can access profile."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_uses_correct_template(self):
        """Test that the profile page uses the correct template."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_shows_user_email(self):
        """Test that the profile displays user email."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertContains(response, "test@example.com")

    def test_profile_shows_security_options(self):
        """Test that the profile shows security options."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertContains(response, "Two-Factor Authentication")
