import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          UdemyClone
        </Link>

        <ul className="navbar-links">
          <li>
            <Link to="/">Courses</Link>
          </li>
          {user ? (
            <>
              {user.role === 'instructor' && (
                <li>
                  <Link to="/instructor">Instructor Dashboard</Link>
                </li>
              )}
              <li>
                <Link to="/dashboard">My Learning</Link>
              </li>
              <li className="user-info">
                <span>Hi, {user.full_name || user.email}</span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" className="btn-login">
                  Log In
                </Link>
              </li>
              <li>
                <Link to="/register" className="btn-signup">
                  Sign Up
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;