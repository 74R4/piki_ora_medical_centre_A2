import { useEffect, useState } from "react";
import API from "../api";

function Doctors() {
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await API.get("doctors/");
      setDoctors(response.data);
    } catch (error) {
      console.error("Error loading doctors:", error);
    }
  };

  return (
    <div className="page">
      <h2>Doctors</h2>

      {doctors.length === 0 ? (
        <p>No doctors found.</p>
      ) : (
        doctors.map((doctor) => (
          <div
            key={doctor.id}
            style={{
              border: "1px solid #ccc",
              marginBottom: "10px",
              padding: "10px",
            }}
          >
            <h3>{doctor.full_name}</h3>

            <p>
              <strong>Specialisation:</strong>{" "}
              {doctor.specialisation}
            </p>

            <p>
              <strong>Email:</strong> {doctor.email}
            </p>

            <p>
              <strong>Phone:</strong> {doctor.phone}
            </p>

            <p>
              <strong>Room:</strong> {doctor.room_number}
            </p>

            <p>{doctor.bio}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default Doctors;