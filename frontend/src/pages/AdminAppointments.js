import { useEffect, useState } from "react";
import API from "../api";

function AdminAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [editingAppointmentId, setEditingAppointmentId] = useState(null);

  const [formData, setFormData] = useState({
    reason: "",
    status: "Booked",
  });

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await API.get("appointments/");
      setAppointments(response.data);
    } catch (error) {
      alert("Only staff users can view this page.");
    }
  };

  const startEdit = (appointment) => {
    setEditingAppointmentId(appointment.id);
    setFormData({
      reason: appointment.reason,
      status: appointment.status,
    });
  };

  const cancelEdit = () => {
    setEditingAppointmentId(null);
    setFormData({
      reason: "",
      status: "Booked",
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const updateAppointment = async (e) => {
    e.preventDefault();

    try {
      await API.patch(`appointments/${editingAppointmentId}/`, formData);
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
      <h2>Manage Appointments</h2>

      {editingAppointmentId && (
        <form onSubmit={updateAppointment} className="card">
          <h3>Edit Appointment</h3>

          <textarea
            name="reason"
            placeholder="Reason"
            value={formData.reason}
            onChange={handleChange}
          />

          <br /><br />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Booked">Booked</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>

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
              <strong>Patient:</strong> {appointment.patient_username}
            </p>

            <p>
              <strong>Date:</strong> {appointment.date}
            </p>

            <p>
              <strong>Time:</strong> {appointment.start_time} - {appointment.end_time}
            </p>

            <p>
              <strong>Reason:</strong> {appointment.reason}
            </p>

            <p>
              <strong>Status:</strong> {appointment.status}
            </p>

            <button onClick={() => startEdit(appointment)}>
              Edit Appointment
            </button>{" "}

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

export default AdminAppointments;
// adding edit/update button