import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = ({ allowedRoles }) => {
  const token = localStorage.getItem('token');
  const userString = localStorage.getItem('user');
  let user = null;

  try {
    user = userString ? JSON.parse(userString) : null;
  } catch (err) {
    console.error("Error parsing user from localStorage", err);
  }

  // If no token exists, redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // If roles are specified and user doesn't match, allow fallback or proceed
  if (allowedRoles && user && user.role && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  // Render child routes directly
  return <Outlet />;
};

export default ProtectedRoute;