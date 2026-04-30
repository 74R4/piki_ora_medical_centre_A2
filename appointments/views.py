from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction

from .models import Doctor, AppointmentSlot, Appointment
from .forms import PatientRegistrationForm, AppointmentBookingForm, AppointmentEditForm


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
def book_appointment(request, slot_id):
    slot = get_object_or_404(
        AppointmentSlot,
        id=slot_id,
        is_available=True,
        appointment__isnull=True
    )

    if request.method == "POST":
        form = AppointmentBookingForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    appointment = form.save(commit=False)
                    appointment.patient = request.user
                    appointment.slot = slot
                    appointment.status = "Booked"
                    appointment.save()

                    slot.is_available = False
                    slot.save()

                messages.success(request, "Your appointment has been booked successfully.")
                return redirect("my_appointments")

            except IntegrityError:
                messages.error(request, "Sorry, this appointment slot has already been booked.")
                return redirect("slot_list")
    else:
        form = AppointmentBookingForm()

    return render(
        request,
        "appointments/book_appointment.html",
        {
            "form": form,
            "slot": slot,
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


@login_required
def edit_my_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user,
        status="Booked"
    )

    old_slot = appointment.slot

    if request.method == "POST":
        form = AppointmentEditForm(request.POST, instance=appointment)

        if form.is_valid():
            updated_appointment = form.save(commit=False)
            new_slot = updated_appointment.slot

            if new_slot != old_slot:
                old_slot.is_available = True
                old_slot.save()

                new_slot.is_available = False
                new_slot.save()

            updated_appointment.save()

            messages.success(request, "Your appointment has been updated successfully.")
            return redirect("my_appointments")
    else:
        form = AppointmentEditForm(instance=appointment)

    return render(
        request,
        "appointments/edit_my_appointment.html",
        {
            "form": form,
            "appointment": appointment,
        }
    )


@login_required
def cancel_my_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user,
        status="Booked"
    )

    if request.method == "POST":
        appointment.status = "Cancelled"
        appointment.save()

        messages.success(request, "Your appointment has been cancelled.")
        return redirect("my_appointments")

    return render(
        request,
        "appointments/cancel_my_appointment.html",
        {"appointment": appointment}
    )