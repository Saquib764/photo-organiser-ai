<script setup lang="ts">
import type { ImageEntry } from '~/types/images'

const props = defineProps<{
  images: ImageEntry[]
  startIndex?: number
}>()

const { rawUrl } = useImageUrls()

const open = defineModel<boolean>('open', { default: false })

const PRELOAD_AHEAD = 10
const preloadedUrls = new Set<string>()

const total = computed(() => props.images.length)

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
    const image = props.images[(fromIndex + offset) % total.value]
    if (image) {
      preloadImage(image.path)
    }
  }

  if (total.value > 1) {
    const previous = props.images[(fromIndex - 1 + total.value) % total.value]
    if (previous) {
      preloadImage(previous.path)
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
  total: () => props.images.length,
  startIndex: () => props.startIndex,
  onIndexChange: preloadAround,
  onOpen: preloadAround,
  onClose: () => {
    preloadedUrls.clear()
  },
})

const currentImage = computed(() => props.images[index.value] ?? null)
const prevImage = computed(() => {
  if (total.value === 0) {
    return null
  }
  return props.images[(index.value - 1 + total.value) % total.value]
})
const nextImage = computed(() => {
  if (total.value === 0) {
    return null
  }
  return props.images[(index.value + 1) % total.value]
})

/** Avoid duplicate Vue keys when only two images (prev === next). */
const showPrevSlide = computed(() => {
  if (!prevImage.value || !nextImage.value || total.value < 2) {
    return false
  }
  return total.value > 2 || prevImage.value.path !== nextImage.value.path
})

const showNextSlide = computed(() => {
  if (!nextImage.value || !prevImage.value || total.value < 2) {
    return false
  }
  return total.value > 2 || prevImage.value.path !== nextImage.value.path
})

watch(
  () => props.images,
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
      aria-label="Image slideshow"
      @mousemove="onPointerActivity"
    >
      <div class="relative min-h-0 flex-1">
        <div
          v-if="currentImage"
          class="slideshow-stage"
        >
          <img
            v-if="showPrevSlide && prevImage"
            :key="prevImage.path"
            :src="rawUrl(prevImage.path)"
            :alt="prevImage.caption || prevImage.path"
            class="slideshow-slide slideshow-slide--prev"
            draggable="false"
          >
          <img
            :key="currentImage.path"
            :src="rawUrl(currentImage.path)"
            :alt="currentImage.caption || currentImage.path"
            class="slideshow-slide slideshow-slide--current"
            draggable="false"
          >
          <img
            v-if="showNextSlide && nextImage"
            :key="nextImage.path"
            :src="rawUrl(nextImage.path)"
            :alt="nextImage.caption || nextImage.path"
            class="slideshow-slide slideshow-slide--next"
            draggable="false"
          >
        </div>

        <header
          v-if="currentImage"
          class="slideshow-chrome slideshow-chrome--top"
          :class="chromeClass"
        >
          <div class="min-w-0 flex-1 space-y-0.5">
            <p class="text-sm font-medium text-gray-100">
              Slideshow
            </p>
            <p
              class="truncate text-xs text-gray-400"
              :title="currentImage.path"
            >
              {{ currentImage.path }}
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
  margin: auto;
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  transition:
    transform 500ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 500ms cubic-bezier(0.4, 0, 0.2, 1);
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
