from django.apps import apps
from django.db import OperationalError, ProgrammingError
from django.utils import timezone

from core.constants import (
    DISPENSARY_BADGE_CLOSED,
    DISPENSARY_BADGE_OPEN,
    DISPENSARY_BADGE_PENDING,
    DISPENSARY_DETAIL_CLOSED,
    DISPENSARY_DETAIL_OPEN,
    DISPENSARY_DETAIL_PENDING,
    DISPENSARY_STATUS_CLOSED,
    DISPENSARY_STATUS_OPEN,
    DISPENSARY_STATUS_PENDING,
)


def dispensary_status(request) -> dict[str, dict[str, str | bool]]:
    """Expose the current dispensary availability badge to all templates."""
    fallback_status = {
        'label': DISPENSARY_STATUS_PENDING,
        'detail': DISPENSARY_DETAIL_PENDING,
        'badge_class': DISPENSARY_BADGE_PENDING,
        'is_open': False,
    }

    try:
        schedule_model = apps.get_model('calendar_app', 'DispensarySchedule', require_ready=False)
    except LookupError:
        return {'dispensary_status': fallback_status}

    try:
        schedule = schedule_model.objects.filter(date=timezone.localdate()).first()
    except (LookupError, OperationalError, ProgrammingError):
        return {'dispensary_status': fallback_status}

    if schedule is None:
        return {
            'dispensary_status': {
                'label': DISPENSARY_STATUS_CLOSED,
                'detail': DISPENSARY_DETAIL_CLOSED,
                'badge_class': DISPENSARY_BADGE_CLOSED,
                'is_open': False,
            }
        }

    if schedule.is_open:
        return {
            'dispensary_status': {
                'label': DISPENSARY_STATUS_OPEN,
                'detail': DISPENSARY_DETAIL_OPEN,
                'badge_class': DISPENSARY_BADGE_OPEN,
                'is_open': True,
            }
        }

    return {
        'dispensary_status': {
            'label': DISPENSARY_STATUS_CLOSED,
            'detail': schedule.note or DISPENSARY_DETAIL_CLOSED,
            'badge_class': DISPENSARY_BADGE_CLOSED,
            'is_open': False,
        }
    }