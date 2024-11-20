import { createContext, useContext, useState } from 'react';
import api from '../lib/axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
 const [user, setUser] = useState(null);

 const login = async (email, password) => {
   const formData = new URLSearchParams();
   formData.append('username', email);
   formData.append('password', password);

   const response = await api.post('/token', formData, {
     headers: {
       'Content-Type': 'application/x-www-form-urlencoded'
     }
   });
   
   localStorage.setItem('token', response.data.access_token);
   setUser(response.data.user);
 };

 const register = async (data) => {
   const response = await api.post('/register/trainer', data);
   return response.data;
 };

 const logout = () => {
   localStorage.removeItem('token');
   setUser(null);
 };

 return (
   <AuthContext.Provider value={{ user, login, register, logout }}>
     {children}
   </AuthContext.Provider>
 );
}

export const useAuth = () => useContext(AuthContext);