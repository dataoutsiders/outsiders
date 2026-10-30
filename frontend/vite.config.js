import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    // Redirige toutes les requêtes vers index.html pour le SPA routing
    historyApiFallback: true,
  },
})
