from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Doctor, AppointmentSlot, Appointment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "specialisation",
            "email",
            "phone",
            "room_number",
            "bio",
            "is_active",
        ]

    def get_full_name(self, obj):
        return f"Dr {obj.first_name} {obj.last_name}"


class AppointmentSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.__str__", read_only=True)
    doctor_specialisation = serializers.CharField(source="doctor.specialisation", read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "doctor_specialisation",
            "date",
            "start_time",
            "end_time",
            "is_available",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source="patient.username", read_only=True)
    doctor_name = serializers.CharField(source="slot.doctor.__str__", read_only=True)
    doctor_specialisation = serializers.CharField(source="slot.doctor.specialisation", read_only=True)
    date = serializers.DateField(source="slot.date", read_only=True)
    start_time = serializers.TimeField(source="slot.start_time", read_only=True)
    end_time = serializers.TimeField(source="slot.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_username",
            "slot",
            "doctor_name",
            "doctor_specialisation",
            "date",
            "start_time",
            "end_time",
            "reason",
            "status",
            "booked_at",
        ]
        read_only_fields = [
            "patient",
            "booked_at",
        ]