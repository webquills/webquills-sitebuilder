"""
Tests for the socialapp management command.
"""

import tempfile
from pathlib import Path

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class CreateSocialAppCommandTests(TestCase):
    """Tests for socialapp management command."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get_current()

    def test_create_new_socialapp(self):
        """Test creating a new SocialApp."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test_secret_key")
            secret_file = f.name

        try:
            call_command(
                "socialapp",
                "--provider",
                "gitea",
                "--name",
                "Test Gitea",
                "--client-id",
                "test_client",
                "--secret-file",
                secret_file,
                "--site-id",
                str(self.site.id),
            )

            # Verify the social app was created
            social_app = SocialApp.objects.get(provider="gitea", name="Test Gitea")
            self.assertEqual(social_app.client_id, "test_client")
            self.assertEqual(social_app.secret, "test_secret_key")
            self.assertIn(self.site, social_app.sites.all())
        finally:
            Path(secret_file).unlink()

    def test_update_existing_socialapp(self):
        """Test updating an existing SocialApp."""
        # Create initial social app
        social_app = SocialApp.objects.create(
            provider="gitea",
            name="Test Gitea",
            client_id="old_client",
            secret="old_secret",
        )
        social_app.sites.add(self.site)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("new_secret_key")
            secret_file = f.name

        try:
            call_command(
                "socialapp",
                "--provider",
                "gitea",
                "--name",
                "Test Gitea",
                "--client-id",
                "new_client",
                "--secret-file",
                secret_file,
            )

            # Verify the social app was updated
            social_app.refresh_from_db()
            self.assertEqual(social_app.client_id, "new_client")
            self.assertEqual(social_app.secret, "new_secret_key")
        finally:
            Path(secret_file).unlink()

    def test_secret_file_not_found(self):
        """Test error handling when secret file doesn't exist."""
        with self.assertRaises(CommandError) as cm:
            call_command(
                "socialapp",
                "--provider",
                "gitea",
                "--name",
                "Test Gitea",
                "--client-id",
                "test_client",
                "--secret-file",
                "/nonexistent/file.txt",
            )
        self.assertIn("Secret file not found", str(cm.exception))

    def test_empty_secret_file(self):
        """Test error handling when secret file is empty."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("")
            secret_file = f.name

        try:
            with self.assertRaises(CommandError) as cm:
                call_command(
                    "socialapp",
                    "--provider",
                    "gitea",
                    "--name",
                    "Test Gitea",
                    "--client-id",
                    "test_client",
                    "--secret-file",
                    secret_file,
                )
            self.assertIn("Secret file is empty", str(cm.exception))
        finally:
            Path(secret_file).unlink()

    def test_site_not_found(self):
        """Test error handling when site doesn't exist."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test_secret")
            secret_file = f.name

        try:
            with self.assertRaises(CommandError) as cm:
                call_command(
                    "socialapp",
                    "--provider",
                    "gitea",
                    "--name",
                    "Test Gitea",
                    "--client-id",
                    "test_client",
                    "--secret-file",
                    secret_file,
                    "--site-id",
                    "9999",
                )
            self.assertIn("Site with ID 9999 does not exist", str(cm.exception))
        finally:
            Path(secret_file).unlink()

    def test_site_not_provided(self):
        """Test creating a SocialApp without providing site-id."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test_secret_no_site")
            secret_file = f.name

        try:
            call_command(
                "socialapp",
                "--provider",
                "gitea",
                "--name",
                "Test Gitea No Site",
                "--client-id",
                "test_client_no_site",
                "--secret-file",
                secret_file,
            )

            # Verify the social app was created without site association
            social_app = SocialApp.objects.get(
                provider="gitea", name="Test Gitea No Site"
            )
            self.assertEqual(social_app.client_id, "test_client_no_site")
            self.assertEqual(social_app.secret, "test_secret_no_site")
            self.assertEqual(social_app.sites.count(), 0)
        finally:
            Path(secret_file).unlink()

    def test_secret_whitespace_stripped(self):
        """Test that whitespace is stripped from secret."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("  test_secret_with_whitespace  \n")
            secret_file = f.name

        try:
            call_command(
                "socialapp",
                "--provider",
                "gitea",
                "--name",
                "Test Gitea",
                "--client-id",
                "test_client",
                "--secret-file",
                secret_file,
            )

            social_app = SocialApp.objects.get(provider="gitea", name="Test Gitea")
            self.assertEqual(social_app.secret, "test_secret_with_whitespace")
        finally:
            Path(secret_file).unlink()
