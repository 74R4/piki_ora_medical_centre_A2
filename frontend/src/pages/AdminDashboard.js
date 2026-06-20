import { useEffect, useState } from "react";
import API from "../api";

function AdminDashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await API.get("dashboard-summary/");
      setSummary(response.data);
    } catch (error) {
      alert("You must be logged in as staff to view this page.");
    }
  };

  if (!summary) {
    return (
      <div className="page">
        <h2>Admin Dashboard</h2>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>Admin Dashboard</h2>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Total Doctors</h3>
          <p>{summary.doctor_count}</p>
        </div>

        <div className="dashboard-card">
          <h3>Total Appointment Slots</h3>
          <p>{summary.slot_count}</p>
        </div>

        <div className="dashboard-card">
          <h3>Total Appointments</h3>
          <p>{summary.appointment_count}</p>
        </div>

        <div className="dashboard-card">
          <h3>Total Patients</h3>
          <p>{summary.patient_count}</p>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;