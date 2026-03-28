
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile

User = get_user_model()


class AccountsFlowTests(TestCase):
    """Regression tests for registration and profile setup."""

    def test_profile_is_created_for_standard_user(self):
        user = User.objects.create_user(username='student1', password='safe-pass-123')

        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, UserProfile.Role.STUDENT)

    def test_profile_is_created_for_superuser_as_admin(self):
        user = User.objects.create_superuser(
            username='admin1',
            email='admin@example.com',
            password='safe-pass-123',
        )

        self.assertEqual(user.profile.role, UserProfile.Role.ADMIN)

    def test_registration_creates_account_and_logs_user_in(self):
        response = self.client.post(
            reverse('accounts:register'),
            data={
                'username': 'alice',
                'first_name': 'Alice',
                'last_name': 'Avery',
                'email': 'alice@example.com',
                'role': UserProfile.Role.STUDENT,
                'roll_number': 'cs-101',
                'phone': '1234567890',
                'year_of_study': 2,
                'password1': 'VerySafePass123',
                'password2': 'VerySafePass123',
            },
        )

        self.assertRedirects(response, reverse('accounts:dashboard'))
        user = User.objects.get(username='alice')
        self.assertEqual(user.profile.roll_number, 'CS-101')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}",
        )

    def test_dashboard_renders_role_specific_copy(self):
        user = User.objects.create_user(username='doctor1', password='safe-pass-123')
        user.profile.role = UserProfile.Role.DOCTOR
        user.profile.save(update_fields=['role'])
        self.client.force_login(user)

        response = self.client.get(reverse('accounts:dashboard'))

        self.assertContains(response, 'Doctor dashboard')
        self.assertContains(response, 'Consultation tools will appear in the next steps.')