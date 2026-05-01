import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction

from .models import Doctor, AppointmentSlot, Appointment
from .forms import (
    PatientRegistrationForm,
    AppointmentBookingForm,
    AppointmentEditForm,
    DoctorForm,
    AppointmentSlotForm,
    PatientAccountForm,
)

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

        appointment.slot.is_available = True
        appointment.slot.save()

        messages.success(request, "Your appointment has been cancelled.")
        return redirect("my_appointments")

    return render(
        request,
        "appointments/cancel_my_appointment.html",
        {"appointment": appointment}
    )

def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user)
def dashboard_home(request):
    doctor_count = Doctor.objects.count()
    slot_count = AppointmentSlot.objects.count()
    appointment_count = Appointment.objects.count()
    patient_count = Appointment.objects.values("patient").distinct().count()

    return render(
        request,
        "appointments/dashboard_home.html",
        {
            "doctor_count": doctor_count,
            "slot_count": slot_count,
            "appointment_count": appointment_count,
            "patient_count": patient_count,
        }
    )


@user_passes_test(is_staff_user)
def dashboard_doctors(request):
    doctors = Doctor.objects.all().order_by("last_name", "first_name")

    return render(
        request,
        "appointments/dashboard_doctors.html",
        {"doctors": doctors}
    )


@user_passes_test(is_staff_user)
def dashboard_doctor_add(request):
    if request.method == "POST":
        form = DoctorForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Doctor profile has been added successfully.")
            return redirect("dashboard_doctors")
    else:
        form = DoctorForm()

    return render(
        request,
        "appointments/dashboard_doctor_form.html",
        {
            "form": form,
            "title": "Add Doctor",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_doctor_edit(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)

        if form.is_valid():
            form.save()
            messages.success(request, "Doctor profile has been updated successfully.")
            return redirect("dashboard_doctors")
    else:
        form = DoctorForm(instance=doctor)

    return render(
        request,
        "appointments/dashboard_doctor_form.html",
        {
            "form": form,
            "title": "Edit Doctor",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_doctor_delete(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        doctor.delete()
        messages.success(request, "Doctor profile has been deleted successfully.")
        return redirect("dashboard_doctors")

    return render(
        request,
        "appointments/dashboard_confirm_delete.html",
        {
            "object_name": f"Dr {doctor.first_name} {doctor.last_name}",
            "cancel_url": "dashboard_doctors",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_slots(request):
    slots = AppointmentSlot.objects.select_related("doctor").order_by("date", "start_time")

    return render(
        request,
        "appointments/dashboard_slots.html",
        {"slots": slots}
    )


@user_passes_test(is_staff_user)
def dashboard_slot_add(request):
    if request.method == "POST":
        form = AppointmentSlotForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Appointment slot has been created successfully.")
            return redirect("dashboard_slots")
    else:
        form = AppointmentSlotForm()

    return render(
        request,
        "appointments/dashboard_slot_form.html",
        {
            "form": form,
            "title": "Add Appointment Slot",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_slot_edit(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)

    if request.method == "POST":
        form = AppointmentSlotForm(request.POST, instance=slot)

        if form.is_valid():
            form.save()
            messages.success(request, "Appointment slot has been updated successfully.")
            return redirect("dashboard_slots")
    else:
        form = AppointmentSlotForm(instance=slot)

    return render(
        request,
        "appointments/dashboard_slot_form.html",
        {
            "form": form,
            "title": "Edit Appointment Slot",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_slot_delete(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)

    if request.method == "POST":
        slot.delete()
        messages.success(request, "Appointment slot has been deleted successfully.")
        return redirect("dashboard_slots")

    return render(
        request,
        "appointments/dashboard_confirm_delete.html",
        {
            "object_name": f"{slot.doctor} on {slot.date} at {slot.start_time}",
            "cancel_url": "dashboard_slots",
        }
    )

@user_passes_test(is_staff_user)
def dashboard_appointments(request):
    appointments = Appointment.objects.select_related(
        "patient",
        "slot",
        "slot__doctor"
    ).order_by("slot__date", "slot__start_time")

    return render(
        request,
        "appointments/dashboard_appointments.html",
        {"appointments": appointments}
    )


@user_passes_test(is_staff_user)
def dashboard_appointment_edit(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    old_slot = appointment.slot

    if request.method == "POST":
        form = AppointmentEditForm(request.POST, instance=appointment)

        if form.is_valid():
            updated_appointment = form.save(commit=False)
            new_slot = updated_appointment.slot

            if updated_appointment.status == "Cancelled":
                old_slot.is_available = True
                old_slot.save()

            elif new_slot != old_slot:
                old_slot.is_available = True
                old_slot.save()

                new_slot.is_available = False
                new_slot.save()

            else:
                new_slot.is_available = False
                new_slot.save()

            updated_appointment.save()

            messages.success(request, "Appointment has been updated successfully.")
            return redirect("dashboard_appointments")
    else:
        form = AppointmentEditForm(instance=appointment)

    return render(
        request,
        "appointments/dashboard_appointment_form.html",
        {
            "form": form,
            "appointment": appointment,
            "title": "Edit Appointment",
        }
    )


@user_passes_test(is_staff_user)
def dashboard_appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        appointment.status = "Cancelled"
        appointment.save()

        appointment.slot.is_available = True
        appointment.slot.save()

        messages.success(request, "Appointment has been cancelled successfully.")
        return redirect("dashboard_appointments")

    return render(
        request,
        "appointments/dashboard_appointment_cancel.html",
        {"appointment": appointment}
    )


@user_passes_test(is_staff_user)
def dashboard_patients(request):
    patients = User.objects.filter(is_staff=False).order_by("last_name", "first_name", "username")

    return render(
        request,
        "appointments/dashboard_patients.html",
        {"patients": patients}
    )


@user_passes_test(is_staff_user)
def dashboard_patient_edit(request, patient_id):
    patient = get_object_or_404(User, id=patient_id, is_staff=False)

    if request.method == "POST":
        form = PatientAccountForm(request.POST, instance=patient)

        if form.is_valid():
            form.save()
            messages.success(request, "Patient account has been updated successfully.")
            return redirect("dashboard_patients")
    else:
        form = PatientAccountForm(instance=patient)

    return render(
        request,
        "appointments/dashboard_patient_form.html",
        {
            "form": form,
            "patient": patient,
            "title": "Edit Patient Account",
        }
    )

def setup_staff_user(request):
    token = request.GET.get("token")
    expected_token = os.environ.get("SETUP_TOKEN")

    if not expected_token or token != expected_token:
        return render(request, "appointments/setup_staff_error.html")

    username = "staff"

    user, created = User.objects.get_or_create(username=username)

    user.first_name = "Piki Ora"
    user.last_name = "Staff"
    user.email = "staff@pikiora.co.nz"
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password("StaffPass123")
    user.save()

    return render(
        request,
        "appointments/setup_staff_success.html",
        {
            "created": created,
            "username": username,
        }
    )