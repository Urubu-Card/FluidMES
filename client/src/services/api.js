import axios from 'axios';


const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true
});

api.interceptors.response.use(
    (response) => {
        // Se a requisição deu certo, apenas retorna a resposta normalmente
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (!error.response|| !originalRequest || !originalRequest.url) {
            return Promise.reject(error);
        }

        if (
            originalRequest.url.includes('/api/login/') || 
            originalRequest.url.includes('/api/me/') || 
            originalRequest.url.includes('/api/auth/refresh/')
        ) {
            return Promise.reject(error);
        }

        // 🔄 REFRESH AUTOMÁTICO: Trata o erro 401 Unauthorized nas demais telas do sistema
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true; 

            try {
                await axios.post('http://localhost:8000/api/auth/refresh/', {}, { withCredentials: true });
                return api(originalRequest);
            } catch (refreshError) {
                window.location.href = '/auth';
                return Promise.reject(refreshError);
            }
        }

        // Retorna qualquer outro tipo de erro (ex: 400 Bad Request, 500 Server Error)
        return Promise.reject(error);
    }
);

export default api;
