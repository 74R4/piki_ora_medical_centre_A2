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
]