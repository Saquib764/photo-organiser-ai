<script setup lang="ts">
const activeTab = useState('document-active-tab', () => 'library')

const tabs = [
  { label: 'Library state', value: 'library', icon: 'i-heroicons-signal' },
  { label: 'Images', value: 'images', icon: 'i-heroicons-photo' },
  { label: 'Photobook', value: 'photobook', icon: 'i-heroicons-book-open' },
  { label: 'Layouts', value: 'layouts', icon: 'i-heroicons-squares-2x2' },
  { label: 'Settings', value: 'settings', icon: 'i-heroicons-cog-6-tooth' },
]
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col overflow-hidden border-t border-gray-800 bg-gray-900">
    <UTabs
      v-model="activeTab"
      :items="tabs"
      variant="link"
      :content="false"
      color="primary"
      class="shrink-0 px-2 pt-1"
      :ui="{
        root: 'w-full',
        list: 'w-full gap-1 border-0 border-b border-gray-800',
        trigger:
          'px-4 py-2 text-xs font-bold uppercase tracking-widest text-gray-500 data-[state=active]:text-white',
        indicator: 'bg-primary-500',
      }"
    />

    <div
      class="min-h-0 flex-1 bg-gray-950"
      :class="
        activeTab === 'images'
          || activeTab === 'settings'
          || activeTab === 'photobook'
          || activeTab === 'layouts'
          ? 'overflow-hidden'
          : 'overflow-y-auto p-6 lg:p-8'
      "
    >
      <LibraryStateTab v-if="activeTab === 'library'" />
      <ImagesTab v-else-if="activeTab === 'images'" />
      <PhotobookTab v-else-if="activeTab === 'photobook'" />
      <LayoutLibraryTab v-else-if="activeTab === 'layouts'" />
      <SettingsTab v-else-if="activeTab === 'settings'" />
    </div>
  </div>
</template>
