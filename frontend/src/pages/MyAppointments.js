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
    }
  };

  return (
    <div className="page">
      <h2>My Appointments</h2>

      {appointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        appointments.map((appointment) => (
          <div
            key={appointment.id}
            style={{
              border: "1px solid #ccc",
              marginBottom: "10px",
              padding: "10px",
            }}
          >
            <h3>{appointment.doctor_name}</h3>

            <p>
              <strong>Date:</strong> {appointment.date}
            </p>

            <p>
              <strong>Time:</strong> {appointment.start_time}
            </p>

            <p>
              <strong>Status:</strong> {appointment.status}
            </p>

            <p>
              <strong>Reason:</strong> {appointment.reason}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

export default MyAppointments;