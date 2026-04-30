from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("slots/", views.slot_list, name="slot_list"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
]