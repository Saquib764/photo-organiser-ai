<script setup lang="ts">
import type { PhotobookPage } from '~/types/photobook'

const { pages } = defineProps<{
  pages: PhotobookPage[]
  openAiConfigured: boolean
  canComposeActivePage: boolean
  canComposeAll: boolean
}>()

const activePageId = defineModel<string | null>('activePageId', { required: true })

const emit = defineEmits<{
  'add-page': []
  'delete-page': [pageId: string]
  'compose-page': []
  'compose-all': []
}>()

const canDeletePage = computed(() => pages.length > 1)

function pageLabel(page: PhotobookPage, index: number) {
  return page.title || `Page ${index + 1}`
}

function statusIcon(page: PhotobookPage) {
  if (page.status === 'ready') {
    return 'i-heroicons-check-circle'
  }
  if (page.status === 'composing') {
    return 'i-heroicons-arrow-path'
  }
  if (page.status === 'error') {
    return 'i-heroicons-exclamation-circle'
  }
  return null
}
</script>

<template>
  <div class="flex shrink-0 items-stretch border-b border-gray-800">
    <div class="tf-scrollbar-hide flex min-w-0 flex-1 items-stretch overflow-x-auto">
      <template
        v-for="(page, index) in pages"
        :key="page.id"
      >
        <div
          v-if="index > 0"
          class="my-2 w-px shrink-0 self-stretch bg-gray-700"
          aria-hidden="true"
        />
        <div
          class="group/tab flex shrink-0 items-center gap-0.5 pr-1.5"
          :class="
            activePageId === page.id
              ? 'bg-gray-900/80 text-white'
              : 'text-gray-500 hover:bg-gray-900/40 hover:text-gray-300'
          "
        >
          <button
            type="button"
            class="flex items-center gap-1.5 py-2.5 pl-4 pr-1 text-xs font-medium whitespace-nowrap transition"
            @click="activePageId = page.id"
          >
            <UIcon
              v-if="statusIcon(page)"
              :name="statusIcon(page)!"
              class="size-3.5 shrink-0"
              :class="{
                'text-primary-400': page.status === 'ready',
                'animate-spin text-gray-400': page.status === 'composing',
                'text-red-400': page.status === 'error',
              }"
            />
            <span>{{ pageLabel(page, index) }}</span>
          </button>
          <button
            v-if="canDeletePage"
            type="button"
            class="flex size-5 shrink-0 items-center justify-center rounded opacity-0 transition hover:bg-gray-700/80 hover:text-white group-hover/tab:opacity-100 focus-visible:opacity-100"
            :class="activePageId === page.id ? 'opacity-60' : ''"
            :aria-label="`Delete ${pageLabel(page, index)}`"
            @click.stop="emit('delete-page', page.id)"
          >
            <UIcon
              name="i-heroicons-x-mark"
              class="size-3.5"
            />
          </button>
        </div>
      </template>
    </div>

    <div
      class="flex shrink-0 items-center gap-2 border-l border-gray-800 bg-gray-950/50 px-3 py-1.5"
    >
      <UButton
        size="xs"
        variant="ghost"
        color="neutral"
        icon="i-heroicons-plus"
        @click="emit('add-page')"
      >
        Add page
      </UButton>
      <UButton
        size="xs"
        variant="soft"
        color="primary"
        icon="i-heroicons-sparkles"
        :disabled="!openAiConfigured || !activePageId || !canComposeActivePage"
        @click="emit('compose-page')"
      >
        Compose page
      </UButton>
      <UButton
        size="xs"
        variant="outline"
        color="primary"
        icon="i-heroicons-squares-2x2"
        :disabled="!openAiConfigured || !canComposeAll"
        @click="emit('compose-all')"
      >
        Compose all
      </UButton>
    </div>
  </div>
</template>
