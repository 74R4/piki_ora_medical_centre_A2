from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),

    path("doctors/", views.doctor_list, name="doctor_list"),
    path("slots/", views.slot_list, name="slot_list"),

    path("book/<int:slot_id>/", views.book_appointment, name="book_appointment"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("my-appointments/<int:appointment_id>/edit/", views.edit_my_appointment, name="edit_my_appointment"),
    path("my-appointments/<int:appointment_id>/cancel/", views.cancel_my_appointment, name="cancel_my_appointment"),

    # Custom administrator dashboard
    path("dashboard/", views.dashboard_home, name="dashboard_home"),

    path("dashboard/doctors/", views.dashboard_doctors, name="dashboard_doctors"),
    path("dashboard/doctors/add/", views.dashboard_doctor_add, name="dashboard_doctor_add"),
    path("dashboard/doctors/<int:doctor_id>/edit/", views.dashboard_doctor_edit, name="dashboard_doctor_edit"),
    path("dashboard/doctors/<int:doctor_id>/delete/", views.dashboard_doctor_delete, name="dashboard_doctor_delete"),

    path("dashboard/slots/", views.dashboard_slots, name="dashboard_slots"),
    path("dashboard/slots/add/", views.dashboard_slot_add, name="dashboard_slot_add"),
    path("dashboard/slots/<int:slot_id>/edit/", views.dashboard_slot_edit, name="dashboard_slot_edit"),
    path("dashboard/slots/<int:slot_id>/delete/", views.dashboard_slot_delete, name="dashboard_slot_delete"),

    path("dashboard/appointments/", views.dashboard_appointments, name="dashboard_appointments"),
    path("dashboard/appointments/<int:appointment_id>/edit/", views.dashboard_appointment_edit,
         name="dashboard_appointment_edit"),
    path("dashboard/appointments/<int:appointment_id>/cancel/", views.dashboard_appointment_cancel,
         name="dashboard_appointment_cancel"),

    path("dashboard/patients/", views.dashboard_patients, name="dashboard_patients"),
    path("dashboard/patients/<int:patient_id>/edit/", views.dashboard_patient_edit, name="dashboard_patient_edit"),
    path("setup-staff/", views.setup_staff_user, name="setup_staff_user"),
]