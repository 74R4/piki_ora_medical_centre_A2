import { useEffect, useState } from "react";
import API from "../api";

function AdminSlots() {
  const [slots, setSlots] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [editingSlotId, setEditingSlotId] = useState(null);

  const [formData, setFormData] = useState({
    doctor: "",
    date: "",
    start_time: "",
    end_time: "",
    is_available: true,
  });

  useEffect(() => {
    fetchSlots();
    fetchDoctors();
  }, []);

  const fetchSlots = async () => {
    try {
      const response = await API.get("slots/");
      setSlots(response.data);
    } catch (error) {
      alert("Only staff users can view this page.");
    }
  };

  const fetchDoctors = async () => {
    try {
      const response = await API.get("doctors/");
      setDoctors(response.data);
    } catch (error) {
      console.error("Could not load doctors.");
    }
  };

  const startEdit = (slot) => {
    setEditingSlotId(slot.id);
    setFormData({
      doctor: slot.doctor,
      date: slot.date,
      start_time: slot.start_time,
      end_time: slot.end_time,
      is_available: slot.is_available,
    });
  };

  const cancelEdit = () => {
    setEditingSlotId(null);
    setFormData({
      doctor: "",
      date: "",
      start_time: "",
      end_time: "",
      is_available: true,
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const updateSlot = async (e) => {
    e.preventDefault();

    try {
      await API.patch(`slots/${editingSlotId}/`, formData);
      alert("Slot updated successfully.");
      cancelEdit();
      fetchSlots();
    } catch (error) {
      alert("Could not update slot. Please check the details.");
    }
  };

  const deleteSlot = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this appointment slot?"
    );

    if (!confirmDelete) return;

    try {
      await API.delete(`slots/${id}/`);
      alert("Slot deleted successfully.");
      fetchSlots();
    } catch (error) {
      alert("Could not delete slot.");
    }
  };

  return (
    <div className="page">
      <h2>Manage Appointment Slots</h2>

      {editingSlotId && (
        <form onSubmit={updateSlot} className="card">
          <h3>Edit Appointment Slot</h3>

          <select
            name="doctor"
            value={formData.doctor}
            onChange={handleChange}
          >
            <option value="">Select doctor</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.full_name}
              </option>
            ))}
          </select>

          <br /><br />

          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
          />

          <br /><br />

          <input
            type="time"
            name="start_time"
            value={formData.start_time}
            onChange={handleChange}
          />

          <br /><br />

          <input
            type="time"
            name="end_time"
            value={formData.end_time}
            onChange={handleChange}
          />

          <br /><br />

          <label>
            <input
              type="checkbox"
              name="is_available"
              checked={formData.is_available}
              onChange={handleChange}
            />
            Slot is available
          </label>

          <br /><br />

          <button type="submit">Update Slot</button>{" "}
          <button type="button" onClick={cancelEdit}>
            Cancel Edit
          </button>
        </form>
      )}

      {slots.length === 0 ? (
        <p>No slots found.</p>
      ) : (
        slots.map((slot) => (
          <div className="card" key={slot.id}>
            <h3>{slot.doctor_name}</h3>

            <p>
              <strong>Date:</strong> {slot.date}
            </p>

            <p>
              <strong>Time:</strong> {slot.start_time} - {slot.end_time}
            </p>

            <p>
              <strong>Available:</strong> {slot.is_available ? "Yes" : "No"}
            </p>

            <button onClick={() => startEdit(slot)}>
              Edit Slot
            </button>{" "}

            <button onClick={() => deleteSlot(slot.id)}>
              Delete Slot
            </button>
          </div>
        ))
      )}
    </div>
  );
}

export default AdminSlots;

// adding edit/update button