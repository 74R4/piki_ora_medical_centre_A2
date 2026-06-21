# Piki Ora Medical Centre Appointment System

## Overview

Piki Ora Medical Centre Appointment System is a full-stack web application developed for Assignment 2.

The system allows patients to:

* Register an account
* Login securely
* View available doctors
* View appointment slots
* Book appointments
* View their appointments
* Cancel appointments

The system allows staff/administrators to:

* Manage doctors
* Manage appointment slots
* Manage appointments
* View dashboard statistics

## Technologies Used

### Frontend

* React
* Axios
* React Router

### Backend

* Django
* Django REST Framework
* Token Authentication

### Database

* PostgreSQL (Neon)

### Deployment

* Frontend: Vercel
* Backend: Vercel

## Features

* User Registration
* User Login
* Token Authentication
* Doctor Management
* Appointment Slot Management
* Appointment Booking
* Appointment Cancellation
* Admin Dashboard
* REST API Integration

## Deployment Links

Frontend:
https://piki-ora-medical-centre-a2-frontend.vercel.app

Backend:
https://piki-ora-medical-centre-a2-backend.vercel.app

## Test Staff Account

Username:
staff

Password:
StaffPass123

## Installation

Backend:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm start
```

## Author
Natara Iata Pimoe
