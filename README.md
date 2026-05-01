# Piki Ora Medical Centre Appointment System

This is a Django web application developed for ISCG7420 Web Application Development Assignment 1 Task 2.

The system allows patients to register, log in, view doctors, view available appointment slots, book appointments, and manage their own appointments.

The system also includes a custom administrator dashboard for authorised staff. The custom dashboard is used instead of relying on the built-in Django Admin site for system management.

## Main Features

### Patient Features
- Patient registration
- Patient login and logout
- View available doctors
- View available appointment slots
- Book an appointment
- View upcoming appointments
- Edit appointment
- Cancel appointment

### Custom Administrator Dashboard Features
- Secure staff-only dashboard
- Add, edit, and delete doctor profiles
- Create, edit, and delete appointment slots
- View all patient appointments
- Edit or cancel patient appointments
- View and manage patient user accounts

## Technical Features

- Django framework
- SQLite database for development
- Django ORM for database access
- Django authentication system
- Role-based access control
- Dynamic templates
- Form handling and validation
- Double-booking prevention using a one-to-one relationship between appointments and appointment slots

## How to Run the Project Locally

1. Create and activate a virtual environment.

2. Install dependencies:

```bash
pip install -r requirements.txt