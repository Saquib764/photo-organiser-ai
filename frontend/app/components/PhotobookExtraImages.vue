<script setup lang="ts">
const props = defineProps<{
  paths: string[]
  focusedSlotId: string | null
  layoutSlotIds: string[]
}>()

const emit = defineEmits<{
  assign: [path: string]
  'update:focusedSlotId': [slotId: string]
}>()

const { rawUrl } = useImageUrls()
const {
  images,
  loadingImages,
  imagesError,
  fetchImages,
  fetchFolders,
} = useImageBrowser()

type PanelTab = 'extras' | 'all'

const panelTab = ref<PanelTab>('extras')
const searchQuery = ref('')

const tabItems = [
  { label: 'Extras', value: 'extras' as const },
  { label: 'All images', value: 'all' as const },
]

const canAssign = computed(
  () => Boolean(props.focusedSlotId && props.layoutSlotIds.length),
)

const filteredAllImages = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) {
    return images.value
  }
  return images.value.filter(
    img =>
      img.path.toLowerCase().includes(q)
      || img.caption.toLowerCase().includes(q)
      || img.folder.toLowerCase().includes(q),
  )
})

const allImagesLabel = computed(() => {
  const total = images.value.length
  const shown = filteredAllImages.value.length
  if (!total) {
    return 'No images in workspace'
  }
  if (shown === total) {
    return `${total} image${total === 1 ? '' : 's'}`
  }
  return `${shown} of ${total} images`
})

watch(panelTab, (tab) => {
  if (tab === 'all' && !images.value.length && !loadingImages.value) {
    void fetchFolders()
    void fetchImages()
  }
})

onMounted(() => {
  if (panelTab.value === 'all') {
    void fetchFolders()
    void fetchImages()
  }
})

function onAssign(path: string) {
  if (canAssign.value) {
    emit('assign', path)
  }
}

function fileName(path: string) {
  return path.split('/').pop() ?? path
}

const imageAssignCardClass
  = 'group relative w-full overflow-hidden rounded-lg border border-gray-800 bg-gray-900 transition hover:border-primary-500/50 disabled:cursor-default disabled:opacity-60'

const imageMetaOverlayClass
  = 'pointer-events-none absolute inset-x-0 bottom-0 z-10 bg-black/75 px-2 py-2 opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-within:opacity-100'
</script>

<template>
  <div class="flex h-full min-h-0 flex-col border-l border-gray-800 bg-gray-900/30">
    <div class="shrink-0 border-b border-gray-800 p-3">
      <h2 class="text-xs font-bold uppercase tracking-widest text-gray-500">
        Assign images
      </h2>
      <UTabs
        v-model="panelTab"
        :items="tabItems"
        :content="false"
        variant="pill"
        color="primary"
        size="xs"
        class="mt-2"
        :ui="{
          list: 'w-full',
          trigger: 'flex-1 justify-center text-[10px] font-bold uppercase tracking-wider',
        }"
      />
      <p class="mt-2 text-xs text-gray-600">
        <template v-if="!canAssign">
          Select a layout slot below to assign an image.
        </template>
        <template v-else-if="panelTab === 'extras'">
          Click an extra to assign to slot “{{ focusedSlotId }}”.
        </template>
        <template v-else>
          Click any image to assign to slot “{{ focusedSlotId }}”.
        </template>
      </p>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto p-3">
      <template v-if="panelTab === 'extras'">
        <div
          v-if="!paths.length"
          class="py-8 text-center text-xs text-gray-600"
        >
          No extra images yet. Compose pages to populate alternates, or pick from All images.
        </div>
        <div
          v-else
          class="flex flex-col gap-2"
        >
          <button
            v-for="path in paths"
            :key="path"
            type="button"
            :class="imageAssignCardClass"
            :disabled="!canAssign"
            @click="onAssign(path)"
          >
            <div class="relative aspect-video w-full">
              <img
                :src="rawUrl(path)"
                :alt="path"
                class="absolute inset-0 size-full object-cover"
                loading="lazy"
                draggable="false"
              >
              <div :class="imageMetaOverlayClass">
                <p class="truncate text-[10px] font-medium text-white">
                  {{ fileName(path) }}
                </p>
              </div>
            </div>
          </button>
        </div>
      </template>

      <template v-else>
        <UInput
          v-model="searchQuery"
          size="xs"
          placeholder="Search images…"
          icon="i-heroicons-magnifying-glass"
          class="mb-2"
        />
        <p class="mb-2 text-[10px] text-gray-600">
          {{ allImagesLabel }}
        </p>

        <div
          v-if="loadingImages"
          class="flex items-center justify-center gap-2 py-8 text-xs text-gray-500"
        >
          <UIcon
            name="i-heroicons-arrow-path"
            class="size-4 animate-spin"
          />
          Loading images…
        </div>

        <UAlert
          v-else-if="imagesError"
          color="error"
          variant="soft"
          :title="imagesError"
          class="mb-2"
        />

        <div
          v-else-if="!filteredAllImages.length"
          class="py-8 text-center text-xs text-gray-600"
        >
          <template v-if="!images.length">
            No images in the workspace. Add folders in the Images tab.
          </template>
          <template v-else>
            No images match your search.
          </template>
        </div>

        <div
          v-else
          class="flex flex-col gap-2"
        >
          <button
            v-for="img in filteredAllImages"
            :key="img.path"
            type="button"
            :class="imageAssignCardClass"
            :disabled="!canAssign"
            @click="onAssign(img.path)"
          >
            <div class="relative aspect-video w-full">
              <img
                :src="rawUrl(img.path)"
                :alt="img.path"
                class="absolute inset-0 size-full object-cover"
                loading="lazy"
                draggable="false"
              >
              <div :class="imageMetaOverlayClass">
                <p class="truncate text-[10px] font-medium text-white">
                  {{ fileName(img.path) }}
                </p>
                <p
                  v-if="img.caption"
                  class="mt-0.5 line-clamp-2 text-[10px] leading-snug text-gray-300"
                >
                  {{ img.caption }}
                </p>
              </div>
            </div>
          </button>
        </div>
      </template>
    </div>

    <div
      v-if="layoutSlotIds.length"
      class="shrink-0 border-t border-gray-800 p-3"
    >
      <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-gray-600">
        Page slots
      </p>
      <div class="flex flex-wrap gap-1">
        <UButton
          v-for="slotId in layoutSlotIds"
          :key="slotId"
          size="xs"
          :variant="focusedSlotId === slotId ? 'solid' : 'ghost'"
          color="primary"
          @click="emit('update:focusedSlotId', slotId)"
        >
          {{ slotId }}
        </UButton>
      </div>
    </div>
  </div>
</template>
