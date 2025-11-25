import axios from "axios";

const API = "http://localhost:8000/users"; // tu backend

export const login = async (username, password) => {
  return await axios.post(`${API}/login/`, { username, password });
};

export const register = async (username, email, password) => {
  return await axios.post(`${API}/register/`, { username, email, password });
};

export const logout = async () => {
  return await axios.post(`${API}/logout/`);
};
