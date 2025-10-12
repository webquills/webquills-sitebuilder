"""Custom adapters for django-allauth."""

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for site-specific customizations."""

    def is_open_for_signup(self, request):
        """Disable open signup (invitation-only)."""
        return False

    def get_login_redirect_url(self, request):
        """Redirect to profile page after successful login."""
        return "/profile/"

    def get_logout_redirect_url(self, request):
        """Redirect to home page on logout."""
        return "/"
