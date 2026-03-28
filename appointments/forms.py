# campuscare/appointments/forms.py — Step 5
from django import forms


class SlotBookingForm(forms.Form):
    """Confirm that the student wants to book the selected slot."""

    confirm_booking = forms.BooleanField(
        label='I confirm that I will arrive on time for this appointment slot.',
        required=True,
    )
