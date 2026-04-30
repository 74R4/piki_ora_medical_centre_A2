from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialisation = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    room_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr {self.first_name} {self.last_name} - {self.specialisation}"


class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointment_slots"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ["doctor", "date", "start_time"]

    def __str__(self):
        return f"{self.doctor} | {self.date} | {self.start_time} - {self.end_time}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Booked", "Booked"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name="appointment"
    )
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Booked"
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slot__date", "slot__start_time"]

    def __str__(self):
        return f"{self.patient.username} booked {self.slot}"