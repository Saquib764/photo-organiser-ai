// https://nuxt.com/docs/api/configuration/nuxt-config
/// <reference types="node" />

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,

  modules: ['@nuxt/eslint', '@nuxt/ui'],

  ui: {
    colorMode: false,
  },

  css: ['~/assets/main.css'],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_API_BASE || 'http://localhost:8001',
      wsUrl: process.env.NUXT_WS_URL || '',
    },
  },

  devServer: {
    port: 80,
  },

  vite: {
    server: {
      // Fail loudly if port 80 is unavailable (e.g. needs sudo on macOS/Linux).
      strictPort: true,
    },
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
      ],
    },
  },
})
