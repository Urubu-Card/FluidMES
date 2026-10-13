import axios from 'axios';

const api = axios.create({
    baseURL: '',
    withCredentials: true,
});

// Rotas que, ao falhar, devem redirecionar direto pra /auth
// (SEM tentar refresh — são rotas de autenticação em si)
const ROTAS_PUBLICAS = [
    '/api/login/',
    '/api/cadastro/',
    '/api/token/refresh/',
];

function isRotaPublica(url) {
    return ROTAS_PUBLICAS.some(rota => url === rota || url.startsWith(rota));
}

// Controle de refresh único (evita múltiplas chamadas simultâneas)
let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(callback) {
    refreshSubscribers.push(callback);
}

function onRefreshed() {
    refreshSubscribers.forEach(callback => callback());
    refreshSubscribers = [];
}

function onRefreshFailed(err) {
    refreshSubscribers.forEach(cb => cb(err));
    refreshSubscribers = [];
}

function redirectToAuth() {
    if (window.location.pathname !== '/auth') {
        window.location.href = '/auth';
    }
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (!error.response || !originalRequest || !originalRequest.url) {
            return Promise.reject(error);
        }

        const url = originalRequest.url;

        // Rotas públicas: nunca tenta refresh, só propaga o erro
        // (quem chama /api/login/ trata a mensagem de erro normalmente)
        if (isRotaPublica(url)) {
            if (url.startsWith('/api/token/refresh/')) {
                redirectToAuth();
            }
            return Promise.reject(error);
        }

        // Rotas protegidas (incluindo /api/me/) passam pelo fluxo de refresh
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            if (isRefreshing) {
                // Já tem um refresh em andamento: espera ele terminar
                return new Promise((resolve, reject) => {
                    subscribeTokenRefresh((err) => {
                        if (err) return reject(err);
                        resolve(api(originalRequest));
                    });
                });
            }

            isRefreshing = true;

            try {
                await axios.post('/api/token/refresh/', {}, { withCredentials: true });
                isRefreshing = false;
                onRefreshed();
                return api(originalRequest);
            } catch (refreshError) {
                isRefreshing = false;
                onRefreshFailed(refreshError);
                //console.error('Falha ao atualizar o token:', refreshError);
                redirectToAuth();
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;