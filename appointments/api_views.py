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


class TemporarySetupAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        setup_token = os.environ.get("SETUP_TOKEN")
        request_token = request.query_params.get("token")

        if not setup_token or request_token != setup_token:
            return Response(
                {"error": "Invalid setup token."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create staff/admin user for marking
        staff_user, created = User.objects.get_or_create(username="staff")
        staff_user.is_staff = True
        staff_user.is_superuser = True
        staff_user.is_active = True
        staff_user.email = "staff@pikiora.co.nz"
        staff_user.first_name = "Staff"
        staff_user.last_name = "Admin"
        staff_user.set_password("StaffPass123")
        staff_user.save()

        doctors_data = [
            {
                "first_name": "Sarah",
                "last_name": "Wilson",
                "specialisation": "General Practitioner",
                "email": "sarah.wilson@pikiora.co.nz",
                "phone": "0211234567",
                "room_number": "Room 1",
                "bio": "Dr Sarah Wilson provides general health consultations for patients.",
            },
            {
                "first_name": "Michael",
                "last_name": "Brown",
                "specialisation": "Cardiology",
                "email": "michael.brown@pikiora.co.nz",
                "phone": "0211111111",
                "room_number": "Room 2",
                "bio": "Dr Michael Brown specialises in heart and cardiovascular conditions.",
            },
            {
                "first_name": "Emma",
                "last_name": "Taylor",
                "specialisation": "Dermatology",
                "email": "emma.taylor@pikiora.co.nz",
                "phone": "0212222222",
                "room_number": "Room 3",
                "bio": "Dr Emma Taylor specialises in skin health and treatment.",
            },
            {
                "first_name": "James",
                "last_name": "Anderson",
                "specialisation": "Paediatrics",
                "email": "james.anderson@pikiora.co.nz",
                "phone": "0213333333",
                "room_number": "Room 4",
                "bio": "Dr James Anderson provides healthcare services for children.",
            },
            {
                "first_name": "Olivia",
                "last_name": "Martin",
                "specialisation": "Orthopaedics",
                "email": "olivia.martin@pikiora.co.nz",
                "phone": "0214444444",
                "room_number": "Room 5",
                "bio": "Dr Olivia Martin specialises in bone and joint conditions.",
            },
            {
                "first_name": "William",
                "last_name": "Lee",
                "specialisation": "Neurology",
                "email": "william.lee@pikiora.co.nz",
                "phone": "0215555555",
                "room_number": "Room 6",
                "bio": "Dr William Lee specialises in disorders of the nervous system.",
            },
        ]

        doctors = []

        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.update_or_create(
                email=doctor_data["email"],
                defaults={
                    "first_name": doctor_data["first_name"],
                    "last_name": doctor_data["last_name"],
                    "specialisation": doctor_data["specialisation"],
                    "phone": doctor_data["phone"],
                    "room_number": doctor_data["room_number"],
                    "bio": doctor_data["bio"],
                    "is_active": True,
                },
            )
            doctors.append(doctor)

        slots_data = [
            (0, date(2026, 7, 1), time(9, 0), time(9, 30)),
            (0, date(2026, 7, 1), time(10, 0), time(10, 30)),
            (1, date(2026, 7, 1), time(9, 0), time(9, 30)),
            (1, date(2026, 7, 1), time(11, 0), time(11, 30)),
            (2, date(2026, 7, 2), time(9, 30), time(10, 0)),
            (3, date(2026, 7, 2), time(10, 30), time(11, 0)),
            (4, date(2026, 7, 3), time(9, 0), time(9, 30)),
            (5, date(2026, 7, 3), time(10, 0), time(10, 30)),
        ]

        for doctor_index, slot_date, start_time, end_time in slots_data:
            AppointmentSlot.objects.get_or_create(
                doctor=doctors[doctor_index],
                date=slot_date,
                start_time=start_time,
                defaults={
                    "end_time": end_time,
                    "is_available": True,
                },
            )

        return Response(
            {
                "message": "Temporary setup completed successfully.",
                "staff_username": "staff",
                "staff_password": "StaffPass123",
                "doctor_count": Doctor.objects.count(),
                "slot_count": AppointmentSlot.objects.count(),
                "patient_count": User.objects.filter(is_staff=False).count(),
            }
        )