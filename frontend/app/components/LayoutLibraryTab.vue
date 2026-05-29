<script setup lang="ts">
import { PhotobookLayoutRenderer } from '~/components/renderer'
import {
  PAGE_LAYOUT_CATEGORIES,
  PAGE_LAYOUTS,
  type PageLayoutCategory,
} from '~/constants/pageLayouts'
import type { PageLayoutDefinition } from '~/types/pageLayoutRender'
import { assignDemoSlots } from '~/utils/layoutPreviewSlots'
import { defaultTextSlotsFromLayout } from '~/utils/photobookTextSlots'

const { images, loadingImages, error } = useImageBrowser()
const { rawUrl } = useImageUrls()
const { aspectRatio } = usePhotobookUiPrefs()

const shuffleSeed = ref(0)
const searchQuery = ref('')
const categoryFilter = ref<PageLayoutCategory | 'all'>('all')

const categoryOptions = [
  { label: 'All', value: 'all' as const },
  { label: 'Grids', value: 'grids' as const },
  { label: 'Cover', value: 'cover' as const },
  { label: 'Wedding', value: 'wedding' as const },
]

const imagePaths = computed(() => images.value.map(img => img.path))

const filteredLayouts = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  let list: PageLayoutDefinition[] = PAGE_LAYOUTS

  if (categoryFilter.value !== 'all') {
    list = PAGE_LAYOUT_CATEGORIES[categoryFilter.value]
  }

  if (!q) {
    return [...list].sort((a, b) => a.name.localeCompare(b.name))
  }

  return list
    .filter(
      layout =>
        layout.id.toLowerCase().includes(q)
        || layout.name.toLowerCase().includes(q)
        || layout.description.toLowerCase().includes(q),
    )
    .sort((a, b) => a.name.localeCompare(b.name))
})

function demoSlots(layout: PageLayoutDefinition) {
  return assignDemoSlots(layout, imagePaths.value, shuffleSeed.value)
}

function demoTextSlots(layout: PageLayoutDefinition) {
  return defaultTextSlotsFromLayout(layout)
}

function shufflePreviews() {
  shuffleSeed.value += 1
}

const layoutCountLabel = computed(() => {
  const n = filteredLayouts.value.length
  const total = PAGE_LAYOUTS.length
  return n === total ? `${total} layouts` : `${n} of ${total} layouts`
})

const previewAspectClass = computed(() => {
  switch (aspectRatio.value) {
    case '9:16':
      return 'aspect-[9/16]'
    case '1:1':
      return 'aspect-square'
    case '16:9':
    default:
      return 'aspect-video'
  }
})

/** Columns per row follow header aspect ratio: landscape 2, square 2, vertical 3. */
const gridColsClass = computed(() => {
  switch (aspectRatio.value) {
    case '9:16':
      return 'grid-cols-3'
    case '1:1':
    case '16:9':
    default:
      return 'grid-cols-2'
  }
})
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <header class="shrink-0 border-b border-gray-800 px-4 py-2 lg:px-6">

      <div class="mt-1 flex flex-col gap-3 sm:flex-row sm:items-center">
        <UInput
          v-model="searchQuery"
          size="sm"
          placeholder="Search layouts…"
          icon="i-heroicons-magnifying-glass"
          class="w-full sm:max-w-xs"
        />
        <div class="flex flex-wrap gap-1.5">
          <UButton
            v-for="opt in categoryOptions"
            :key="opt.value"
            size="xs"
            :color="categoryFilter === opt.value ? 'primary' : 'neutral'"
            :variant="categoryFilter === opt.value ? 'soft' : 'ghost'"
            @click="categoryFilter = opt.value"
          >
            {{ opt.label }}
          </UButton>
        </div>
      </div>

      <UAlert
        v-if="error"
        color="error"
        variant="soft"
        :title="error"
        class="mt-3"
      />
      <UAlert
        v-else-if="!loadingImages && !imagePaths.length"
        color="warning"
        variant="soft"
        title="No gallery images"
        description="Add folders in the Images tab or check your workspace paths. Layouts still render with placeholders."
        class="mt-3"
      />
    </header>

    <div class="min-h-0 flex-1 overflow-y-auto p-4 lg:p-6">
      <div
        v-if="loadingImages && !filteredLayouts.length"
        class="flex items-center justify-center py-24 text-sm text-gray-500"
      >
        Loading…
      </div>

      <div
        v-else-if="!filteredLayouts.length"
        class="flex flex-col items-center justify-center gap-2 py-24 text-center"
      >
        <UIcon
          name="i-heroicons-squares-2x2"
          class="size-10 text-gray-600"
        />
        <p class="text-sm text-gray-500">
          No layouts match your search.
        </p>
      </div>

      <div
        v-else
        class="grid gap-5"
        :class="gridColsClass"
      >
        <article
          v-for="layout in filteredLayouts"
          :key="layout.id"
          tabindex="0"
          class="group flex items-center justify-center rounded-lg border border-gray-800 bg-gray-900/60 px-3 py-4 outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50"
        >
          <div
            class="relative mx-auto w-full max-h-[40vh] overflow-hidden bg-white"
            :class="previewAspectClass"
          >
            <div class="absolute inset-0">
              <PhotobookLayoutRenderer
                :layout-id="layout.id"
                :slots="demoSlots(layout)"
                :text-slots="demoTextSlots(layout)"
                :image-url="rawUrl"
                :editable="false"
              />
            </div>

            <div
              class="absolute inset-x-0 bottom-0 z-10 select-text bg-black/75 px-3 py-3 opacity-0 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100"
            >
              <h3 class="truncate text-sm font-medium text-white">
                {{ layout.name }}
              </h3>
              <p class="mt-0.5 truncate font-mono text-[10px] text-gray-400">
                {{ layout.id }}
              </p>
              <div class="mt-1.5 flex flex-wrap gap-1">
                <UBadge
                  size="xs"
                  color="neutral"
                  variant="subtle"
                >
                  {{ layout.category }}
                </UBadge>
                <UBadge
                  v-if="layout.page_role"
                  size="xs"
                  color="primary"
                  variant="subtle"
                >
                  {{ layout.page_role }}
                </UBadge>
                <UBadge
                  size="xs"
                  color="neutral"
                  variant="outline"
                >
                  {{ layout.slots.length }} photo{{ layout.slots.length === 1 ? '' : 's' }}
                </UBadge>
                <UBadge
                  v-if="layout.text_slots?.length"
                  size="xs"
                  color="neutral"
                  variant="outline"
                >
                  {{ layout.text_slots.length }} text
                </UBadge>
              </div>
              <p
                v-if="layout.description"
                class="mt-2 line-clamp-2 text-[11px] leading-relaxed text-gray-400"
              >
                {{ layout.description }}
              </p>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>
