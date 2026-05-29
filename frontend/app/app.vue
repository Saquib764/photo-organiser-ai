<script setup lang="ts">
import { useHead, useSeoMeta } from '#app'

import { googleFontsStylesheetUrl } from '~/constants/typography/google-fonts'

useHead({
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { name: 'theme-color', content: '#030712' },
    { name: 'color-scheme', content: 'dark' },
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' },
    {
      rel: 'stylesheet',
      href: googleFontsStylesheetUrl(),
    },
  ],
  htmlAttrs: {
    lang: 'en',
    class: 'scheme-dark',
  },
  bodyAttrs: {
    class: 'scheme-dark bg-gray-950 text-gray-200',
  },
})

useSeoMeta({
  title: 'Photo Organiser',
  description: 'Organise your photos into beautiful albums with AI',
})
</script>

<template>
  <UApp>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
