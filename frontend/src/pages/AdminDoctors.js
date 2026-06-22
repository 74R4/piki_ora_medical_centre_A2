import { useEffect, useState } from "react";
import API from "../api";

function AdminDoctors() {
  const [doctors, setDoctors] = useState([]);
  const [editingDoctorId, setEditingDoctorId] = useState(null);

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    specialisation: "",
    email: "",
    phone: "",
    room_number: "",
    bio: "",
    is_active: true,
  });

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

  const startEdit = (doctor) => {
    setEditingDoctorId(doctor.id);
    setFormData({
      first_name: doctor.first_name,
      last_name: doctor.last_name,
      specialisation: doctor.specialisation,
      email: doctor.email,
      phone: doctor.phone,
      room_number: doctor.room_number,
      bio: doctor.bio,
      is_active: doctor.is_active,
    });
  };

  const cancelEdit = () => {
    setEditingDoctorId(null);
    setFormData({
      first_name: "",
      last_name: "",
      specialisation: "",
      email: "",
      phone: "",
      room_number: "",
      bio: "",
      is_active: true,
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const updateDoctor = async (e) => {
    e.preventDefault();

    try {
      await API.patch(`doctors/${editingDoctorId}/`, formData);
      alert("Doctor updated successfully.");
      cancelEdit();
      fetchDoctors();
    } catch (error) {
      alert("Could not update doctor.");
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

      {editingDoctorId && (
        <form onSubmit={updateDoctor} className="card">
          <h3>Edit Doctor</h3>

          <input
            name="first_name"
            placeholder="First name"
            value={formData.first_name}
            onChange={handleChange}
          />
          <br /><br />

          <input
            name="last_name"
            placeholder="Last name"
            value={formData.last_name}
            onChange={handleChange}
          />
          <br /><br />

          <input
            name="specialisation"
            placeholder="Specialisation"
            value={formData.specialisation}
            onChange={handleChange}
          />
          <br /><br />

          <input
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
          />
          <br /><br />

          <input
            name="phone"
            placeholder="Phone"
            value={formData.phone}
            onChange={handleChange}
          />
          <br /><br />

          <input
            name="room_number"
            placeholder="Room number"
            value={formData.room_number}
            onChange={handleChange}
          />
          <br /><br />

          <textarea
            name="bio"
            placeholder="Bio"
            value={formData.bio}
            onChange={handleChange}
          />
          <br /><br />

          <label>
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
            />
            Active doctor
          </label>

          <br /><br />

          <button type="submit">Update Doctor</button>{" "}
          <button type="button" onClick={cancelEdit}>
            Cancel Edit
          </button>
        </form>
      )}

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

            <button onClick={() => startEdit(doctor)}>
              Edit Doctor
            </button>{" "}

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