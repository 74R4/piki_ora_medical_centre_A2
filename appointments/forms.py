from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Doctor, AppointmentSlot, Appointment


class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "first_name",
            "last_name",
            "specialisation",
            "email",
            "phone",
            "room_number",
            "bio",
            "is_active",
        ]


class AppointmentSlotForm(forms.ModelForm):
    class Meta:
        model = AppointmentSlot
        fields = [
            "doctor",
            "date",
            "start_time",
            "end_time",
            "is_available",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 4}),
        }


class AppointmentEditForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["slot", "reason", "status"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_slot = self.instance.slot if self.instance and self.instance.pk else None

        available_slots = AppointmentSlot.objects.filter(
            is_available=True,
            appointment__isnull=True
        )

        if current_slot:
            available_slots = available_slots | AppointmentSlot.objects.filter(pk=current_slot.pk)

        self.fields["slot"].queryset = available_slots.order_by("date", "start_time")

class PatientAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]