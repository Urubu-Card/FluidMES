    import axios from 'axios';

    const api = axios.create({
        baseURL: '',
        withCredentials: true
    });

    api.interceptors.response.use(
        (response) => response,
        async (error) => {
            const originalRequest = error.config;

            if (!error.response || !originalRequest || !originalRequest.url) {
                return Promise.reject(error);
            }

            // Se o ERRO veio da própria rota de refresh ou login, cancela na hora.
            // Isso impede o loop infinito caso o refresh retorne 401.
            if (
                originalRequest.url.includes('/api/login/') ||
                originalRequest.url.includes('/api/token/refresh/')
            ) {
                // Se falhou o refresh, força o redirecionamento imediato
                // (só redireciona se ainda não estiver na tela de auth,
                // para não recarregar a página em loop infinito)
                if (originalRequest.url.includes('/api/token/refresh/')) {
                    if (window.location.pathname !== '/auth') {
                        window.location.href = '/auth';
                    }
                }
                return Promise.reject(error);
            }

            // 🔄 REFRESH AUTOMÁTICO (Para /api/me/ e outras rotas do sistema)
            if (error.response.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;

                try {
                    // Renova o token usando a baseURL correta
                    await axios.post(`${api.defaults.baseURL}/api/token/refresh/`, {}, { withCredentials: true });

                    // Refaz a requisição original (ex: /api/me/) com o novo token/cookie
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