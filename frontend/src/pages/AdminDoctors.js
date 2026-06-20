import { useEffect, useState } from "react";
import API from "../api";

function AdminDoctors() {
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await API.get("doctors/");
      setDoctors(response.data);
    } catch (error) {
      alert("Only staff users can view this page.");
    }
  };

  const deleteDoctor = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this doctor?"
    );

    if (!confirmDelete) return;

    try {
      await API.delete(`doctors/${id}/`);
      alert("Doctor deleted successfully.");
      fetchDoctors();
    } catch (error) {
      alert("Could not delete doctor.");
    }
  };

  return (
    <div className="page">
      <h2>Manage Doctors</h2>

      {doctors.length === 0 ? (
        <p>No doctors found.</p>
      ) : (
        doctors.map((doctor) => (
          <div className="card" key={doctor.id}>
            <h3>{doctor.full_name}</h3>
            <p><strong>Specialisation:</strong> {doctor.specialisation}</p>
            <p><strong>Email:</strong> {doctor.email}</p>
            <p><strong>Phone:</strong> {doctor.phone}</p>
            <p><strong>Room:</strong> {doctor.room_number}</p>
            <p><strong>Active:</strong> {doctor.is_active ? "Yes" : "No"}</p>

            <button onClick={() => deleteDoctor(doctor.id)}>
              Delete Doctor
            </button>
          </div>
        ))
      )}
    </div>
  );
}

export default AdminDoctors;