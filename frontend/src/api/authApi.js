import API from './axios';

export const loginUser = async (credentials) => {
  // Pass credentials directly as a JSON object
  const response = await API.post('/auth/login', {
    email: credentials.email,
    password: credentials.password,
  });
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await API.post('/auth/register', userData);
  return response.data;
};

export const fetchUserProfile = async () => {
  const response = await API.get('/auth/me');
  return response.data;
};