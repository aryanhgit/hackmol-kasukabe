
from django import forms
from django.forms import formset_factory

from consultation.models import Prescription


class PrescriptionForm(forms.ModelForm):
    """Capture the presenting symptoms for a consultation."""

    class Meta:
        model = Prescription
        fields = ('symptoms',)
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 5}),
        }


class PrescriptionMedicineForm(forms.Form):
    """Capture one medicine row on a prescription."""

    medicine_name = forms.CharField(max_length=120)
    dosage_instructions = forms.CharField(max_length=255)
    quantity = forms.IntegerField(min_value=1)


PrescriptionMedicineFormSet = formset_factory(
    PrescriptionMedicineForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
