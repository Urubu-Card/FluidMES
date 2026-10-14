import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // URL do backend usada pelo proxy de desenvolvimento (padrão: API local na porta 8000).
  const env = loadEnv(mode, process.cwd(), '');
  const api = env.VITE_DEV_API_TARGET || 'http://127.0.0.1:8000';
  const ws = api.replace(/^http/, 'ws');
  return {
    plugins: [react()],
    server: { proxy: {
      '/api': { target: api, changeOrigin: false },
      '/ws': { target: ws, ws: true, changeOrigin: false },
    } },
  };
});
