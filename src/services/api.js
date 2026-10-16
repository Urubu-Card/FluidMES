import axios from 'axios';
const options = { baseURL: import.meta.env.VITE_API_URL || '', withCredentials: true, timeout: 15000 };
const transport = axios.create(options);
const api = axios.create(options);
let csrfPromise;
let refreshPromise;
async function csrfToken() {
    if (!csrfPromise) csrfPromise = transport.get('/api/csrf/').then(r => r.data.csrfToken).catch(e => { csrfPromise = undefined; throw e; });
    return csrfPromise;
}
api.interceptors.request.use(async config => {
    if (!['get', 'head', 'options'].includes(config.method)) config.headers['X-CSRFToken'] = await csrfToken();
    return config;
});
const publicPaths = ['/api/login/', '/api/cadastro/', '/api/password-reset/', '/api/logout/', '/api/csrf/'];
api.interceptors.response.use(r => r, async error => {
    const config = error.config;
    if (error.response?.status !== 401 || !config || config._retry || publicPaths.some(p => config.url.startsWith(p))) throw error;
    config._retry = true;
    try {
        if (!refreshPromise) refreshPromise = csrfToken().then(token => transport.post('/api/token/refresh/', {}, { headers: { 'X-CSRFToken': token } })).finally(() => { refreshPromise = undefined; });
        await refreshPromise;
        return api(config);
    } catch (refreshError) {
        if (window.location.pathname.startsWith('/app')) window.location.assign('/auth');
        throw refreshError;
    }
});
export default api;
