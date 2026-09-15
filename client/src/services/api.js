import axios from 'axios';

const api = axios.create({
    /*baseURL: 'https://serverfluidmes.vercel.app',*/
    baseURL: '',
    withCredentials: true,
})

const ROTAS_PUBLICAS = [
    '/api/login/',
    '/api/cadastro/',
    '/api/token/refresh/',
    '/api/me/',
];

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (!error.response || !originalRequest || !originalRequest.url) {
            return Promise.reject(error);
        }

        const isRotaPublica = ROTAS_PUBLICAS.some(rota =>
            originalRequest.url.includes(rota)
        );

        if (isRotaPublica) {
            // Se falhou o refresh, força redirecionamento (sem loop)
            if (originalRequest.url.includes('/api/token/refresh/')) {
                if (window.location.pathname !== '/auth') {
                    window.location.href = '/auth';
                }
            }
            return Promise.reject(error);
        }

        // 🔄 REFRESH AUTOMÁTICO (para rotas protegidas)
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                await axios.post(`${api.defaults.baseURL}/api/token/refresh/`, {}, { withCredentials: true });
                return api(originalRequest);
            } catch (refreshError) {
                if (window.location.pathname !== '/auth') {
                    window.location.href = '/auth';
                }
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);
export default api;