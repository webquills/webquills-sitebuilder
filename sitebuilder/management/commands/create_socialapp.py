"""
Django management command to create or update a SocialApp.

This command allows creating or updating a django-allauth SocialApp
with credentials read from a file to avoid exposing secrets in command history.
"""

from pathlib import Path

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update a SocialApp with credentials from a file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--provider",
            type=str,
            required=True,
            help="Provider ID (e.g., 'github', 'gitea')",
        )
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="Name for the social app",
        )
        parser.add_argument(
            "--client-id",
            type=str,
            required=True,
            help="Client ID for the social app",
        )
        parser.add_argument(
            "--secret-file",
            type=str,
            required=True,
            help="Path to file containing the secret key",
        )
        parser.add_argument(
            "--site-id",
            type=int,
            default=1,
            help="Site ID to associate with the social app (default: 1)",
        )

    def handle(self, *args, **options):
        provider = options["provider"]
        name = options["name"]
        client_id = options["client_id"]
        secret_file = Path(options["secret_file"])
        site_id = options["site_id"]

        # Read secret from file
        if not secret_file.exists():
            raise CommandError(f"Secret file not found: {secret_file}")

        try:
            secret = secret_file.read_text().strip()
        except Exception as e:
            raise CommandError(f"Failed to read secret file: {e}") from e

        if not secret:
            raise CommandError("Secret file is empty")

        # Get or create the site
        try:
            site = Site.objects.get(pk=site_id)
        except Site.DoesNotExist as e:
            raise CommandError(f"Site with ID {site_id} does not exist") from e

        # Get or create the social app
        social_app, created = SocialApp.objects.get_or_create(
            provider=provider,
            name=name,
            defaults={
                "client_id": client_id,
                "secret": secret,
            },
        )

        if not created:
            # Update existing social app
            social_app.client_id = client_id
            social_app.secret = secret
            social_app.save()
            self.stdout.write(
                self.style.SUCCESS(f"Updated SocialApp '{name}' for provider '{provider}'")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Created SocialApp '{name}' for provider '{provider}'")
            )

        # Add site to social app if not already added
        if not social_app.sites.filter(pk=site_id).exists():
            social_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f"Associated with site {site.domain}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Already associated with site {site.domain}"))
