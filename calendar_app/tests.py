# campuscare/calendar_app/tests.py — Step 4
from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from calendar_app.models import DispensarySchedule
from core.context_processors import dispensary_status

User = get_user_model()


class CalendarScheduleTests(TestCase):
    """Regression tests for the dispensary calendar module."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_open_schedule_requires_valid_time_window(self):
        schedule = DispensarySchedule(
            date=timezone.localdate(),
            is_open=True,
            open_time=time(hour=14, minute=0),
            close_time=time(hour=9, minute=0),
        )

        with self.assertRaises(ValidationError):
            schedule.full_clean()

    def test_context_processor_reports_open_schedule(self):
        DispensarySchedule.objects.create(
            date=timezone.localdate(),
            is_open=True,
            open_time=time(hour=9, minute=0),
            close_time=time(hour=17, minute=0),
            note='General consultation day',
        )
        request = self.factory.get('/')

        context = dispensary_status(request)

        self.assertEqual(context['dispensary_status']['label'], 'Open today')
        self.assertTrue(context['dispensary_status']['is_open'])

    def test_month_view_requires_login(self):
        response = self.client.get(reverse('calendar:month'))

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('calendar:month')}")

    def test_month_view_renders_for_authenticated_user(self):
        user = User.objects.create_user(username='calendar-user', password='safe-pass-123')
        self.client.force_login(user)

        response = self.client.get(reverse('calendar:month'))

        self.assertContains(response, 'Dispensary calendar')

    def test_manage_view_is_restricted_to_admins(self):
        user = User.objects.create_user(username='student-user', password='safe-pass-123')
        self.client.force_login(user)

        response = self.client.get(reverse('calendar:manage'))

        self.assertEqual(response.status_code, 403)

    def test_manage_view_saves_schedule_for_admin(self):
        admin_user = User.objects.create_superuser(
            username='calendar-admin',
            email='calendar-admin@example.com',
            password='safe-pass-123',
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse('calendar:manage'),
            data={
                'date': timezone.localdate().isoformat(),
                'is_open': 'on',
                'open_time': '09:00',
                'close_time': '16:00',
                'note': 'Main dispensary hours',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(DispensarySchedule.objects.count(), 1)
