import { useEffect, useState } from "react";
import API from "../api";

function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);

  useEffect(() => {
    fetchDoctors();
    fetchSlots();
  }, []);

  const fetchDoctors = async () => {
    const response = await API.get("doctors/");
    setDoctors(response.data);
  };

  const fetchSlots = async () => {
    const response = await API.get("slots/");
    setSlots(response.data);
  };

  const bookSlot = async (slotId) => {
    const reason = prompt("Enter appointment reason:");

    if (!reason) return;

    try {
      await API.post("appointments/", {
        slot: slotId,
        reason: reason,
      });

      alert("Appointment booked successfully.");
      fetchSlots();
    } catch (error) {
      alert("This slot is not available or you need to log in.");
    }
  };

  return (
    <div className="page">
      <h2>Doctors and Available Slots</h2>

      {doctors.map((doctor) => (
        <div key={doctor.id} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "15px" }}>
          <h3>{doctor.full_name}</h3>
          <p><strong>Specialisation:</strong> {doctor.specialisation}</p>
          <p><strong>Room:</strong> {doctor.room_number}</p>
          <p>{doctor.bio}</p>

          <h4>Available Slots</h4>

          {slots.filter((slot) => slot.doctor === doctor.id).length === 0 ? (
            <p>No available slots.</p>
          ) : (
            slots
              .filter((slot) => slot.doctor === doctor.id)
              .map((slot) => (
                <div key={slot.id}>
                  <p>
                    {slot.date} | {slot.start_time} - {slot.end_time}
                    {" "}
                    <button onClick={() => bookSlot(slot.id)}>Book</button>
                  </p>
                </div>
              ))
          )}
        </div>
      ))}
    </div>
  );
}

export default Doctors;