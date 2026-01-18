// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
  ],

  app: {
    head: {
      title: 'Emo-Check | エモ度判定アプリ',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AIがあなたの写真の「エモさ」を数値化。さらにエモく加工してSNSでシェアしよう。' },
        { property: 'og:title', content: 'Emo-Check | エモ度判定アプリ' },
        { property: 'og:description', content: 'AIがあなたの写真の「エモさ」を数値化。さらにエモく加工してSNSでシェアしよう。' },
        { name: 'theme-color', content: '#1a1a1a' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap' },
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || 'http://localhost:8000',
    },
  },

  css: ['~/assets/css/main.css'],
})
