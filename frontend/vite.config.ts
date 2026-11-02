import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  // .app.github.dev lets the dev server accept GitHub Codespaces forwarded-port hostnames.
  server: { host: true, port: 5173, allowedHosts: ['.app.github.dev'] },
});
