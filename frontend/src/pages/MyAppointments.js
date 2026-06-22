import { useEffect, useState } from "react";
import API from "../api";

function MyAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [editingAppointmentId, setEditingAppointmentId] = useState(null);
  const [reason, setReason] = useState("");

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

  const startEdit = (appointment) => {
    setEditingAppointmentId(appointment.id);
    setReason(appointment.reason);
  };

  const cancelEdit = () => {
    setEditingAppointmentId(null);
    setReason("");
  };

  const updateAppointment = async (e) => {
    e.preventDefault();

    try {
      await API.patch(`appointments/${editingAppointmentId}/`, {
        reason: reason,
      });

      alert("Appointment updated successfully.");
      cancelEdit();
      fetchAppointments();
    } catch (error) {
      alert("Could not update appointment.");
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

      {editingAppointmentId && (
        <form onSubmit={updateAppointment} className="card">
          <h3>Edit Appointment Reason</h3>

          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Update appointment reason"
          />

          <br /><br />

          <button type="submit">Update Appointment</button>{" "}
          <button type="button" onClick={cancelEdit}>
            Cancel Edit
          </button>
        </form>
      )}

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
              <>
                <button onClick={() => startEdit(appointment)}>
                  Edit Appointment
                </button>{" "}

                <button onClick={() => cancelAppointment(appointment.id)}>
                  Cancel Appointment
                </button>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default MyAppointments;