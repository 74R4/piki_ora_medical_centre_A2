import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/">Piki Ora Medical Centre</Link>
      <Link to="/doctors">Doctors</Link>

      {user && <Link to="/my-appointments">My Appointments</Link>}
      {user?.is_staff && <Link to="/admin">Admin Dashboard</Link>}

      {!user ? (
        <>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </>
      ) : (
        <button onClick={logout}>Logout</button>
      )}
    </nav>
  );
}

export default Navbar;