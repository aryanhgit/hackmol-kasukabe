# campuscare/accounts/views.py — Step 1
# campuscare/accounts/views.py — Step 2
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView

from accounts.forms import RegistrationForm
from accounts.models import UserProfile
# from core.decorators import RoleRequiredMixin


class RegistrationView(CreateView):
    """Register a new user, create the profile, and sign them in."""

    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        self.object = user
        login(self.request, user)
        messages.success(self.request, 'Your CampusCare account has been created.')
        return HttpResponseRedirect(self.get_success_url())


class CampusCareLoginView(LoginView):
    """Authenticate a user and send them to the role-aware dashboard."""

    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Welcome back to CampusCare.')
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.get_redirect_url() or reverse('accounts:dashboard')


class CampusCareLogoutView(LogoutView):
    """End the session and return the user to the login page."""

    next_page = reverse_lazy('accounts:login')


class DashboardRedirectView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """Show the user the appropriate starting point for their role."""

    template_name = 'accounts/dashboard_redirect.html'
    allowed_roles = tuple(UserProfile.Role.values)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile

        role_copy = {
            UserProfile.Role.STUDENT: {
                'heading': 'Student dashboard',
                'summary': 'Book appointments and follow your token status as those modules come online.',
                'primary_action_label': None,
                'primary_action_url': None,
            },
            UserProfile.Role.DOCTOR: {
                'heading': 'Doctor dashboard',
                'summary': 'Consultation tools will appear in the next steps. Your account is ready now.',
                'primary_action_label': None,
                'primary_action_url': None,
            },
            UserProfile.Role.PHARMACIST: {
                'heading': 'Pharmacist dashboard',
                'summary': 'Dispense and inventory tools will be connected in later steps.',
                'primary_action_label': None,
                'primary_action_url': None,
            },
            UserProfile.Role.ADMIN: {
                'heading': 'Admin dashboard',
                'summary': 'Use the Django admin while calendar, inventory, and analytics modules are added.',
                'primary_action_label': 'Open admin',
                'primary_action_url': reverse('admin:index'),
            },
        }

        context['profile'] = profile
        context['dashboard_copy'] = role_copy[profile.role]
        return context