import { useEffect, useState } from "react";
import API from "../api";

function MyAppointments() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await API.get("appointments/");
      setAppointments(response.data);
    } catch (error) {
      console.error(error);
      alert("Please log in to view your appointments.");
    }
  };

  const cancelAppointment = async (id) => {
    const confirmCancel = window.confirm(
      "Are you sure you want to cancel this appointment?"
    );

    if (!confirmCancel) return;

    try {
      await API.post(`appointments/${id}/cancel/`);
      alert("Appointment cancelled successfully.");
      fetchAppointments();
    } catch (error) {
      alert("Could not cancel appointment.");
    }
  };

  return (
    <div className="page">
      <h2>My Appointments</h2>

      {appointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        appointments.map((appointment) => (
          <div className="card" key={appointment.id}>
            <h3>{appointment.doctor_name}</h3>

            <p>
              <strong>Date:</strong> {appointment.date}
            </p>

            <p>
              <strong>Time:</strong> {appointment.start_time} - {appointment.end_time}
            </p>

            <p>
              <strong>Status:</strong> {appointment.status}
            </p>

            <p>
              <strong>Reason:</strong> {appointment.reason}
            </p>

            {appointment.status !== "Cancelled" && (
              <button onClick={() => cancelAppointment(appointment.id)}>
                Cancel Appointment
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default MyAppointments;