<script setup lang="ts">
import { PhotobookLayoutRenderer } from '~/components/renderer'
import type { PhotobookAspectRatio } from '~/composables/usePhotobookUiPrefs'
import type { PhotobookPage } from '~/types/photobook'
import { canRenderPageLayout } from '~/utils/pageLayoutRender'

const props = defineProps<{
  pages: PhotobookPage[]
  aspectRatio: PhotobookAspectRatio
  startIndex?: number
}>()

const { rawUrl } = useImageUrls()

const open = defineModel<boolean>('open', { default: false })

const PRELOAD_AHEAD = 10
const preloadedUrls = new Set<string>()

const total = computed(() => props.pages.length)

function collectPageImagePaths(page: PhotobookPage): string[] {
  return Object.values(page.slots ?? {}).filter(Boolean)
}

function preloadImage(path: string) {
  const url = rawUrl(path)
  if (preloadedUrls.has(url)) {
    return
  }
  preloadedUrls.add(url)
  const img = new Image()
  img.src = url
}

function preloadAround(fromIndex: number) {
  if (total.value === 0) {
    return
  }

  const ahead = Math.min(PRELOAD_AHEAD, total.value - 1)
  for (let offset = 1; offset <= ahead; offset++) {
    const page = props.pages[(fromIndex + offset) % total.value]
    if (page) {
      for (const path of collectPageImagePaths(page)) {
        preloadImage(path)
      }
    }
  }

  if (total.value > 1) {
    const previous = props.pages[(fromIndex - 1 + total.value) % total.value]
    if (previous) {
      for (const path of collectPageImagePaths(previous)) {
        preloadImage(path)
      }
    }
  }
}

const {
  index,
  playing,
  isFullscreen,
  rootRef,
  positionLabel,
  chromeClass,
  onPointerActivity,
  togglePlay,
  toggleFullscreen,
  close,
  startTimer,
} = useSlideshowViewer(open, {
  total: () => props.pages.length,
  startIndex: () => props.startIndex,
  onIndexChange: preloadAround,
  onOpen: preloadAround,
  onClose: () => {
    preloadedUrls.clear()
  },
})

const currentPage = computed(() => props.pages[index.value] ?? null)
const prevPage = computed(() => {
  if (total.value === 0) {
    return null
  }
  return props.pages[(index.value - 1 + total.value) % total.value]
})
const nextPage = computed(() => {
  if (total.value === 0) {
    return null
  }
  return props.pages[(index.value + 1) % total.value]
})

const showPrevSlide = computed(() => total.value >= 2 && !!prevPage.value)
const showNextSlide = computed(() => total.value >= 2 && !!nextPage.value)

const aspectClass = computed(() => {
  switch (props.aspectRatio) {
    case '9:16':
      return 'aspect-[9/16]'
    case '1:1':
      return 'aspect-square'
    case '16:9':
    default:
      return 'aspect-video'
  }
})

function pageLabel(page: PhotobookPage, pageIndex: number) {
  return page.title || `Page ${pageIndex + 1}`
}

const currentPageLabel = computed(() => {
  const page = currentPage.value
  if (!page) {
    return ''
  }
  return pageLabel(page, index.value)
})

function hasRenderableLayout(page: PhotobookPage) {
  return canRenderPageLayout(page.layout_id)
}

function sheetStyle(page: PhotobookPage) {
  return page.background_color
    ? { backgroundColor: page.background_color }
    : {}
}

watch(
  () => props.pages,
  () => {
    preloadedUrls.clear()
    if (open.value) {
      preloadAround(index.value)
      startTimer()
    }
  },
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      ref="rootRef"
      class="fixed inset-0 z-[200] flex flex-col bg-gray-950 text-white"
      role="dialog"
      aria-modal="true"
      aria-label="Photobook slideshow"
      @mousemove="onPointerActivity"
    >
      <div class="relative min-h-0 flex-1">
        <div
          v-if="currentPage"
          class="slideshow-stage"
        >
          <div
            v-if="showPrevSlide && prevPage"
            :key="`prev-${prevPage.id}`"
            class="slideshow-slide slideshow-slide--prev slideshow-page-slide"
          >
            <div class="relative flex min-h-0 size-full items-center justify-center overflow-hidden p-6">
              <div
                class="relative h-full max-h-full w-full max-w-full overflow-hidden"
                :class="aspectClass"
                :style="sheetStyle(prevPage)"
              >
                <div class="absolute inset-0">
                  <PhotobookLayoutRenderer
                    v-if="hasRenderableLayout(prevPage)"
                    :layout-id="prevPage.layout_id"
                    :slots="prevPage.slots"
                    :text-slots="prevPage.text_slots ?? {}"
                    :slot-offsets="prevPage.slot_offsets ?? {}"
                    :image-url="rawUrl"
                    :image-border-radius="prevPage.image_border_radius"
                    :editable="false"
                  />
                  <div
                    v-else
                    class="flex h-full min-h-[200px] w-full flex-col items-center justify-center gap-2 p-8 text-center"
                  >
                    <p class="text-sm font-semibold text-white">
                      {{ prevPage.title || 'Untitled page' }}
                    </p>
                    <p class="text-xs text-gray-400">
                      No layout yet. Chat to plan pages, then compose to assign photos.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            :key="`current-${currentPage.id}`"
            class="slideshow-slide slideshow-slide--current slideshow-page-slide"
          >
            <div class="relative flex min-h-0 size-full items-center justify-center overflow-hidden p-6">
              <div
                class="relative h-full max-h-full w-full max-w-full overflow-hidden"
                :class="aspectClass"
                :style="sheetStyle(currentPage)"
              >
                <div class="absolute inset-0">
                  <PhotobookLayoutRenderer
                    v-if="hasRenderableLayout(currentPage)"
                    :layout-id="currentPage.layout_id"
                    :slots="currentPage.slots"
                    :text-slots="currentPage.text_slots ?? {}"
                    :slot-offsets="currentPage.slot_offsets ?? {}"
                    :image-url="rawUrl"
                    :image-border-radius="currentPage.image_border_radius"
                    :editable="false"
                  />
                  <div
                    v-else
                    class="flex h-full min-h-[200px] w-full flex-col items-center justify-center gap-2 p-8 text-center"
                  >
                    <p class="text-sm font-semibold text-white">
                      {{ currentPage.title || 'Untitled page' }}
                    </p>
                    <p class="text-xs text-gray-400">
                      No layout yet. Chat to plan pages, then compose to assign photos.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="showNextSlide && nextPage"
            :key="`next-${nextPage.id}`"
            class="slideshow-slide slideshow-slide--next slideshow-page-slide"
          >
            <div class="relative flex min-h-0 size-full items-center justify-center overflow-hidden p-6">
              <div
                class="relative h-full max-h-full w-full max-w-full overflow-hidden"
                :class="aspectClass"
                :style="sheetStyle(nextPage)"
              >
                <div class="absolute inset-0">
                  <PhotobookLayoutRenderer
                    v-if="hasRenderableLayout(nextPage)"
                    :layout-id="nextPage.layout_id"
                    :slots="nextPage.slots"
                    :text-slots="nextPage.text_slots ?? {}"
                    :slot-offsets="nextPage.slot_offsets ?? {}"
                    :image-url="rawUrl"
                    :image-border-radius="nextPage.image_border_radius"
                    :editable="false"
                  />
                  <div
                    v-else
                    class="flex h-full min-h-[200px] w-full flex-col items-center justify-center gap-2 p-8 text-center"
                  >
                    <p class="text-sm font-semibold text-white">
                      {{ nextPage.title || 'Untitled page' }}
                    </p>
                    <p class="text-xs text-gray-400">
                      No layout yet. Chat to plan pages, then compose to assign photos.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <header
          v-if="currentPage"
          class="slideshow-chrome slideshow-chrome--top"
          :class="chromeClass"
        >
          <div class="min-w-0 flex-1 space-y-0.5">
            <p class="text-sm font-medium text-gray-100">
              Photobook slideshow
            </p>
            <p
              class="truncate text-xs text-gray-400"
              :title="currentPageLabel"
            >
              {{ currentPageLabel }}
            </p>
            <p class="tabular-nums text-xs text-gray-300">
              {{ positionLabel }}
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-1">
            <UButton
              :icon="playing ? 'i-heroicons-pause' : 'i-heroicons-play'"
              color="primary"
              variant="solid"
              size="sm"
              :label="playing ? 'Pause' : 'Play'"
              @click="togglePlay"
            />
            <UButton
              :icon="isFullscreen ? 'i-heroicons-arrows-pointing-in' : 'i-heroicons-arrows-pointing-out'"
              color="neutral"
              variant="solid"
              size="sm"
              :label="isFullscreen ? 'Exit fullscreen' : 'Fullscreen'"
              :aria-label="isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'"
              @click="toggleFullscreen"
            />
            <UButton
              icon="i-heroicons-x-mark"
              color="neutral"
              variant="ghost"
              aria-label="Close slideshow"
              @click="close"
            />
          </div>
        </header>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.slideshow-chrome {
  position: absolute;
  inset-inline: 0;
  z-index: 20;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  transition: opacity 300ms ease;
}

.slideshow-chrome--top {
  top: 0;
  align-items: center;
  background: linear-gradient(to bottom, rgb(0 0 0 / 0.75), rgb(0 0 0 / 0.35), transparent);
}

.slideshow-chrome--visible {
  opacity: 1;
  pointer-events: auto;
}

.slideshow-chrome--hidden {
  opacity: 0;
  pointer-events: none;
}

.slideshow-stage {
  position: relative;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.slideshow-slide {
  position: absolute;
  inset: 0;
  transition:
    transform 500ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

.slideshow-page-slide {
  display: flex;
  align-items: center;
  justify-content: center;
}

.slideshow-slide--prev {
  opacity: 0;
  transform: translateX(-100%);
  z-index: 0;
}

.slideshow-slide--current {
  opacity: 1;
  transform: translateX(0);
  z-index: 1;
}

.slideshow-slide--next {
  opacity: 0;
  transform: translateX(100%);
  z-index: 0;
}
</style>
