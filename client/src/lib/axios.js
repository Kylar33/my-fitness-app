import axios from "axios";

const api = axios.create({
 baseURL: "http://localhost:8000/api/v1",
 headers: {
   'Content-Type': 'application/json',
   'Accept': 'application/json'
 }
});

// Request interceptor
api.interceptors.request.use(
 (config) => {
   const token = localStorage.getItem("token");
   if (token) {
     config.headers.Authorization = `Bearer ${token}`;
   }
   
   // Manejo especial para peticiones form-urlencoded
   if (config.url === '/token') {
     config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
   }
   
   return config;
 },
 (error) => {
   return Promise.reject(error);
 }
);

// Response interceptor
api.interceptors.response.use(
 (response) => response,
 async (error) => {
   const originalRequest = error.config;

   if (error.response?.status === 401 && !originalRequest._retry) {
     originalRequest._retry = true;
     localStorage.removeItem("token");
     window.location.href = "/login";
   }

   if (error.response?.status === 422) {
     console.error("Validation error:", error.response.data);
   }

   return Promise.reject(error);
 }
);

export const endpoints = {
 users: '/users',
 routines: '/routines',
 nutritionPlans: '/nutrition-plans',
 stats: '/stats',
 profile: '/users/me',
 trainers: '/dashboard',
};

export default api;