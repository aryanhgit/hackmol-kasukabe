from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView

from accounts.forms import RegistrationForm, StudentRegistrationForm
from accounts.models import UserProfile
from accounts.services import (
    build_admin_dashboard,
    build_doctor_dashboard,
    build_pharmacist_dashboard,
    build_student_dashboard,
)
from core.constants import AVG_CONSULT_MINUTES, QUEUE_POLL_INTERVAL_MS
from core.decorators import RoleRequiredMixin


class RegistrationView(CreateView):
    """Register a new user, create the profile, and sign them in."""

    form_class = RegistrationForm
    template_name = 'accounts/register_doctor_pharma.html'
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != UserProfile.Role.ADMIN:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        self.object = user

        messages.success(self.request, 'Registration successful.')
        return HttpResponseRedirect(self.get_success_url())
    
class StudentRegistrationView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'accounts/register_student.html'
    success_url = reverse_lazy('accounts:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != UserProfile.Role.ADMIN:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        self.object = user

        messages.success(self.request, 'Student registered successfully.')
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
                'summary': 'Book appointments and track your token status.',
                'actions': [], 
            },
            UserProfile.Role.DOCTOR: {
                'heading': 'Doctor dashboard',
                'summary': 'Manage consultations and patient queue.',
                'actions': [], 
            },
            UserProfile.Role.PHARMACIST: {
                'heading': 'Pharmacist dashboard',
                'summary': 'Handle prescriptions and inventory.',
                'actions': [], 
            },
            UserProfile.Role.ADMIN: {
                'heading': 'Admin dashboard',
                'summary': 'Full system control and user management.',
                'actions': [
                    {'label': 'Open Admin Panel', 'url': reverse('admin:index')},
                    {'label': 'Register Student', 'url': reverse('accounts:register_student')},
                    {'label': 'Register Doctor/Pharmacist', 'url': reverse('accounts:register')},
                ],
            },
        }

        context['profile'] = profile
        context['dashboard_copy'] = role_copy.get(profile.role, {})

        context['is_student'] = profile.role == UserProfile.Role.STUDENT
        context['is_doctor'] = profile.role == UserProfile.Role.DOCTOR
        context['is_pharmacist'] = profile.role == UserProfile.Role.PHARMACIST

        return context