# campuscare/appointments/tests.py — Step 5
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Slot, Token
from appointments.services import BookingError, expire_stale_tokens, generate_token, get_queue_snapshot

User = get_user_model()


class AppointmentBookingTests(TestCase):
    """Regression tests for slot booking and queue behavior."""

    def setUp(self):
        self.student_user = User.objects.create_user(username='slot-student', password='safe-pass-123')
        self.student_profile = self.student_user.profile
        self.slot = Slot.objects.create(
            title='General Consultation',
            date=timezone.localdate() + timedelta(days=1),
            start_time=time(hour=10, minute=0),
            end_time=time(hour=10, minute=30),
            max_capacity=2,
            notes='Morning visit window',
        )

    def test_generate_token_creates_waiting_token_with_qr(self):
        token = generate_token(self.student_profile, self.slot)

        self.assertEqual(token.status, Token.Status.WAITING)
        self.assertTrue(token.qr_image)

    def test_generate_token_blocks_double_booking_for_same_student(self):
        generate_token(self.student_profile, self.slot)

        with self.assertRaisesMessage(BookingError, 'You already have an active appointment token.'):
            generate_token(self.student_profile, self.slot)

    def test_expire_stale_tokens_marks_waiting_token_expired(self):
        token = generate_token(self.student_profile, self.slot)
        expired_count = expire_stale_tokens(reference_time=token.expires_at + timedelta(minutes=1))
        token.refresh_from_db()

        self.assertEqual(expired_count, 1)
        self.assertEqual(token.status, Token.Status.EXPIRED)

    def test_queue_snapshot_counts_waiting_students_ahead(self):
        other_user = User.objects.create_user(username='slot-student-two', password='safe-pass-123')
        generate_token(self.student_profile, self.slot)
        other_token = generate_token(other_user.profile, self.slot)

        snapshot = get_queue_snapshot(other_token)

        self.assertEqual(snapshot['waiting_ahead'], 1)
        self.assertEqual(snapshot['queue_position'], 2)

    def test_slot_list_requires_login(self):
        response = self.client.get(reverse('appointments:slot_list'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('appointments:slot_list')}",
        )

    def test_booking_view_creates_token_for_student(self):
        self.client.force_login(self.student_user)

        response = self.client.post(
            reverse('appointments:book', kwargs={'slot_id': self.slot.pk}),
            data={'confirm_booking': True},
        )

        self.assertRedirects(response, reverse('appointments:my_token'))
        self.assertEqual(Token.objects.count(), 1)

    def test_queue_count_returns_live_snapshot(self):
        token = generate_token(self.student_profile, self.slot)
        self.client.force_login(self.student_user)

        response = self.client.get(reverse('appointments:queue_count', kwargs={'token_id': token.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['queue_position'], 1)
