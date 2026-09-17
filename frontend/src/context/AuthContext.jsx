import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, fetchUserProfile } from '../api/authApi';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  // Restore user profile on app startup if a token exists
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const profile = await fetchUserProfile();
          setUser(profile);
        } catch (error) {
          console.error('Failed to load user profile:', error);
          logout();
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  const login = async (credentials) => {
    const data = await loginUser(credentials);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    const profile = await fetchUserProfile();
    setUser(profile);
    return profile;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);