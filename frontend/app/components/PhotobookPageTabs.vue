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
  'reorder-pages': [pageIds: string[]]
  'shuffle-pages': []
}>()

const canDeletePage = computed(() => pages.length > 1)
const canReorder = computed(() => pages.length > 1)

const draggingPageId = ref<string | null>(null)
const dropTargetPageId = ref<string | null>(null)

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

function onDragStart(pageId: string, event: DragEvent) {
  if (!canReorder.value) {
    return
  }
  draggingPageId.value = pageId
  dropTargetPageId.value = pageId
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', pageId)
  }
}

function onDragOver(pageId: string) {
  if (!draggingPageId.value || draggingPageId.value === pageId) {
    return
  }
  dropTargetPageId.value = pageId
}

function onDrop(targetPageId: string) {
  const dragId = draggingPageId.value
  if (!dragId || dragId === targetPageId) {
    return
  }

  const ids = pages.map(page => page.id)
  const from = ids.indexOf(dragId)
  const to = ids.indexOf(targetPageId)
  if (from < 0 || to < 0) {
    return
  }

  const next = [...ids]
  next.splice(from, 1)
  next.splice(to, 0, dragId)
  emit('reorder-pages', next)
}

function onDragEnd() {
  draggingPageId.value = null
  dropTargetPageId.value = null
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
          class="group/tab flex shrink-0 items-center gap-0.5 pr-1.5 transition"
          :class="[
            activePageId === page.id
              ? 'bg-gray-900/80 text-white'
              : 'text-gray-500 hover:bg-gray-900/40 hover:text-gray-300',
            draggingPageId === page.id ? 'opacity-40' : '',
            dropTargetPageId === page.id && draggingPageId && draggingPageId !== page.id
              ? 'ring-1 ring-inset ring-primary-500/60'
              : '',
          ]"
          @dragover.prevent="onDragOver(page.id)"
          @drop.prevent="onDrop(page.id)"
        >
          <button
            v-if="canReorder"
            type="button"
            class="ml-1 flex size-6 shrink-0 cursor-grab items-center justify-center rounded text-gray-600 transition hover:bg-gray-800/80 hover:text-gray-300 active:cursor-grabbing"
            :aria-label="`Drag ${pageLabel(page, index)}`"
            draggable="true"
            @dragstart="onDragStart(page.id, $event)"
            @dragend="onDragEnd"
            @click.stop
          >
            <UIcon
              name="i-heroicons-bars-3"
              class="size-3.5"
            />
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 py-2.5 pl-2 pr-1 text-xs font-medium whitespace-nowrap transition"
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
        v-if="canReorder"
        size="xs"
        variant="ghost"
        color="neutral"
        icon="i-heroicons-arrows-right-left"
        title="Shuffle page order"
        @click="emit('shuffle-pages')"
      >
        Shuffle
      </UButton>
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
