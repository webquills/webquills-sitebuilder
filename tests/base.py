"""Base test case and utilities for testing."""

from django.contrib.sites.models import Site
from django.test import TestCase, override_settings


@override_settings(SITE_ID=1)
class SiteBuilderTestCase(TestCase):
    """Base test case that sets up Site object required by django-allauth."""

    @classmethod
    def setUpTestData(cls):
        """Set up the Site object once for all tests in the class."""
        super().setUpTestData()
        # Create a Site object required by django.contrib.sites and allauth
        Site.objects.get_or_create(
            pk=1, defaults={"domain": "testserver", "name": "Test Site"}
        )
