<script setup lang="ts">
import { PhotobookLayoutRenderer } from '~/components/renderer'
import { getPageLayout } from '~/constants/pageLayouts'
import type { PhotobookPage, SlotOffset } from '~/types/photobook'
import { canRenderPageLayout } from '~/utils/pageLayoutRender'

const props = defineProps<{
  page: PhotobookPage | null
  aspectRatio?: '9:16' | '1:1' | '16:9'
}>()

const emit = defineEmits<{
  setImageBorderRadius: [radius: number]
  setBackgroundColor: [color: string]
  slotOffsetChange: [slotId: string, offset: SlotOffset]
  textSlotChange: [slotId: string, text: string]
}>()

const { rawUrl } = useImageUrls()

const selectedColor = computed(
  () => props.page?.background_color?.toLowerCase() ?? '',
)

const pageLayout = computed(() =>
  props.page?.layout_id ? getPageLayout(props.page.layout_id) : undefined,
)

const hasRenderableLayout = computed(() => canRenderPageLayout(props.page?.layout_id))

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

const sheetStyle = computed(() =>
  props.page?.background_color
    ? { backgroundColor: props.page.background_color }
    : {},
)

const imageBorderRadius = computed({
  get: () => props.page?.image_border_radius ?? 0,
  set: (value: number) => emit('setImageBorderRadius', value),
})

const MAX_IMAGE_BORDER_RADIUS = 48
</script>

<template>
  <div
    v-if="!page"
    class="flex flex-1 items-center justify-center text-sm text-gray-500"
  >
    Select a page
  </div>
  <div
    v-else
    class="flex min-h-0 flex-1 flex-col"
  >
    <div class="shrink-0 border-b border-gray-800 px-4 py-3">
      <h3 class="text-sm font-semibold text-white">
        {{ page.title }}
      </h3>
      <p
        v-if="page.narrative"
        class="mt-1 text-xs text-gray-500"
      >
        {{ page.narrative }}
      </p>
      <div
        v-if="page.layout_id"
        class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-2"
      >
        <p class="shrink-0 text-xs text-primary-400/80">
          Layout: {{ page.layout_id.replace(/_/g, ' ') }}
          <span
            v-if="pageLayout?.page_role"
            class="ml-1 text-gray-500"
          >
            · {{ pageLayout.page_role }} page
          </span>
        </p>
        <div
          v-if="page.palette_colors?.length"
          class="flex items-center gap-2"
        >
          <span class="shrink-0 text-xs text-gray-500">Sheet</span>
          <div class="flex items-center gap-1.5">
            <button
              v-for="hex in page.palette_colors"
              :key="hex"
              type="button"
              class="size-6 shrink-0 rounded border-2 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
              :class="selectedColor === hex.toLowerCase()
                ? 'border-white ring-1 ring-primary-400'
                : 'border-gray-700 hover:border-gray-500'"
              :style="{ backgroundColor: hex }"
              :title="hex"
              :aria-label="`Use sheet color ${hex}`"
              :aria-pressed="selectedColor === hex.toLowerCase()"
              @click="emit('setBackgroundColor', hex)"
            />
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="shrink-0 text-xs text-gray-500">Corners</span>
          <USlider
            v-model="imageBorderRadius"
            :min="0"
            :max="MAX_IMAGE_BORDER_RADIUS"
            :step="1"
            size="xs"
            class="w-[100px] shrink-0"
          />
          <span class="w-9 shrink-0 text-right text-xs tabular-nums text-gray-500">
            {{ imageBorderRadius }}px
          </span>
        </div>
      </div>
    </div>

    <UAlert
      v-if="page.layout_error"
      color="warning"
      variant="soft"
      :title="page.layout_error"
      description="This page uses an unknown layout template. Re-plan in chat or pick a layout after compose."
      class="shrink-0"
    />

    <UAlert
      v-if="page.status === 'error' && page.error_message"
      color="error"
      variant="soft"
      :title="page.error_message"
      class="shrink-0"
    />

    <div class="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden p-4">
      <div
        class="relative h-full max-h-full w-full max-w-full overflow-hidden"
        :class="aspectClass"
        :style="sheetStyle"
      >
        <PhotobookLayoutRenderer
          v-if="hasRenderableLayout"
          :layout-id="page.layout_id!"
          :slots="page.slots"
          :text-slots="page.text_slots ?? {}"
          :slot-offsets="page.slot_offsets ?? {}"
          :image-url="rawUrl"
          :image-border-radius="imageBorderRadius"
          :editable="page.status !== 'composing'"
          @slot-offset-change="(slotId, offset) => emit('slotOffsetChange', slotId, offset)"
          @text-slot-change="(slotId, text) => emit('textSlotChange', slotId, text)"
        />
      </div>
    </div>

    <div
      v-if="!page.layout_id"
      class="flex flex-1 flex-col items-center justify-center gap-2 border border-dashed border-gray-800 bg-gray-900/30 p-8 text-center"
    >
      <UIcon
        name="i-heroicons-sparkles"
        class="size-8 text-gray-600"
      />
      <p class="text-sm text-gray-500">
        No layout yet. Chat to plan pages, then compose to assign photos and text.
      </p>
    </div>
    <div
      v-else-if="!hasRenderableLayout"
      class="flex flex-1 flex-col items-center justify-center gap-2 border border-dashed border-gray-800 bg-gray-900/30 p-8 text-center"
    >
      <UIcon
        name="i-heroicons-exclamation-triangle"
        class="size-8 text-amber-600"
      />
      <p class="text-sm text-gray-400">
        Unknown layout <span class="font-mono text-gray-300">{{ page.layout_id }}</span>.
        Re-plan in chat or update the page layout library.
      </p>
    </div>
  </div>
</template>
