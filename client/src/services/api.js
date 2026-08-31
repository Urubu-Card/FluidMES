import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true
})

// api.interceptors.request.use(
//     (config) => {
//         const token = localStorage.getItem('@api:token');
//         if (token) {
//             config.headers.Authorization = `Bearer ${token}`;
//         }
//         return config;
//     },
//     (error) => {
//         return Promise.reject(error);
//     }
// );


api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('@api:token');
            localStorage.removeItem('@api:refresh');
            
            window.location.href ='/auth';
            
        }
        return Promise.reject(error);
    }
);

export default api;