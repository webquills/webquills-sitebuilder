from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "index.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view - requires authentication."""

    template_name = "profile.html"
    login_url = "/"
