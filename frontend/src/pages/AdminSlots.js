import { useEffect, useState } from "react";
import API from "../api";

function AdminSlots() {
  const [slots, setSlots] = useState([]);

  useEffect(() => {
    fetchSlots();
  }, []);

  const fetchSlots = async () => {
    try {
      const response = await API.get("slots/");
      setSlots(response.data);
    } catch (error) {
      alert("Only staff users can view this page.");
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