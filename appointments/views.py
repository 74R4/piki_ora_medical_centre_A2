from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Doctor, AppointmentSlot, Appointment
from .forms import PatientRegistrationForm


def home(request):
    return render(request, "appointments/home.html")


def register(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("doctor_list")
    else:
        form = PatientRegistrationForm()

    return render(request, "appointments/register.html", {"form": form})


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).order_by("last_name", "first_name")

    return render(request, "appointments/doctor_list.html", {"doctors": doctors})


@login_required
def slot_list(request):
    doctor_id = request.GET.get("doctor")

    slots = AppointmentSlot.objects.filter(
        is_available=True,
        appointment__isnull=True,
        date__gte=timezone.localdate()
    ).select_related("doctor").order_by("date", "start_time")

    if doctor_id:
        slots = slots.filter(doctor_id=doctor_id)

    doctors = Doctor.objects.filter(is_active=True).order_by("last_name", "first_name")

    return render(
        request,
        "appointments/slot_list.html",
        {
            "slots": slots,
            "doctors": doctors,
            "selected_doctor": doctor_id,
        }
    )


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("slot", "slot__doctor").order_by("slot__date", "slot__start_time")

    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments}
    )