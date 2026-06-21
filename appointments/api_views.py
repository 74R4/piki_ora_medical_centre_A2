import os
from datetime import date, time
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, AppointmentSlot, Appointment
from .permissions import IsAdminOrReadOnly, IsAdminUserOnly, IsOwnerOrAdmin
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DoctorSerializer,
    AppointmentSlotSerializer,
    AppointmentSerializer,
)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "message": "Account created successfully.",
                    "token": token.key,
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"error": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "user": UserSerializer(user).data,
            }
        )


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAdminUserOnly]

    def get(self, request):
        return Response(
            {
                "doctor_count": Doctor.objects.count(),
                "slot_count": AppointmentSlot.objects.count(),
                "appointment_count": Appointment.objects.count(),
                "patient_count": User.objects.filter(is_staff=False).count(),
            }
        )


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Doctor.objects.all().order_by("last_name", "first_name")

        return Doctor.objects.filter(is_active=True).order_by("last_name", "first_name")


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = AppointmentSlot.objects.select_related("doctor").order_by("date", "start_time")

        # Normal patients should only see future available slots.
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(
                is_available=True,
                appointment__isnull=True,
                date__gte=timezone.localdate(),
                doctor__is_active=True,
            )

        doctor_id = self.request.query_params.get("doctor")

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        return queryset


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "patient",
            "slot",
            "slot__doctor",
        ).order_by("slot__date", "slot__start_time")

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(patient=self.request.user)

    def perform_create(self, serializer):
        slot = serializer.validated_data["slot"]

        if not slot.is_available:
            raise IntegrityError("This slot is not available.")

        serializer.save(patient=self.request.user, status="Booked")

    def create(self, request, *args, **kwargs):
        slot_id = request.data.get("slot")

        try:
            slot = AppointmentSlot.objects.get(
                id=slot_id,
                is_available=True,
                appointment__isnull=True,
            )
        except AppointmentSlot.DoesNotExist:
            return Response(
                {"error": "Sorry, this appointment slot is not available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    appointment = serializer.save(
                        patient=request.user,
                        slot=slot,
                        status="Booked",
                    )

                    slot.is_available = False
                    slot.save()

                return Response(
                    self.get_serializer(appointment).data,
                    status=status.HTTP_201_CREATED,
                )

            except IntegrityError:
                return Response(
                    {"error": "Sorry, this appointment slot has already been booked."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        old_slot = appointment.slot

        serializer = self.get_serializer(
            appointment,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            new_slot = serializer.validated_data.get("slot", old_slot)
            new_status = serializer.validated_data.get("status", appointment.status)

            if new_slot != old_slot:
                if not new_slot.is_available:
                    return Response(
                        {"error": "The selected new slot is not available."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            with transaction.atomic():
                updated_appointment = serializer.save()

                if new_status == "Cancelled":
                    old_slot.is_available = True
                    old_slot.save()

                elif new_slot != old_slot:
                    old_slot.is_available = True
                    old_slot.save()

                    new_slot.is_available = False
                    new_slot.save()

            return Response(self.get_serializer(updated_appointment).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        appointment.status = "Cancelled"
        appointment.save()

        appointment.slot.is_available = True
        appointment.slot.save()

        return Response(
            {
                "message": "Appointment cancelled successfully.",
                "appointment": self.get_serializer(appointment).data,
            }
        )


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUserOnly]

    def get_queryset(self):
        return User.objects.filter(is_staff=False).order_by(
            "last_name",
            "first_name",
            "username",
        )
