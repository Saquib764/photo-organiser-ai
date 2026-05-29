<script setup lang="ts">
import { getPageLayout } from '~/constants/pageLayouts'
import type { SlotOffset, TextSlotValue } from '~/types/photobook'

import PhotobookRenderNode from './PhotobookRenderNode.vue'
import PhotobookSlotCell from './PhotobookSlotCell.vue'

const props = defineProps<{
  layoutId: string
  slots: Record<string, string>
  textSlots?: Record<string, TextSlotValue>
  slotOffsets?: Record<string, SlotOffset>
  imageUrl: (path: string) => string
  imageBorderRadius?: number
  editable?: boolean
}>()

defineEmits<{
  slotOffsetChange: [slotId: string, offset: SlotOffset]
  textSlotChange: [slotId: string, text: string]
}>()

const layout = computed(() => getPageLayout(props.layoutId))

const unknownSlotKeys = computed(() =>
  Object.keys(props.slots ?? {}).filter(k => Boolean(props.slots[k])),
)

const imageRadiusStyle = computed(() => ({
  borderRadius: `${props.imageBorderRadius ?? 0}px`,
}))

function offsetFor(slotId: string): SlotOffset | undefined {
  return props.slotOffsets?.[slotId]
}
</script>

<template>
  <PhotobookRenderNode
    v-if="layout"
    :node="layout.render"
    :slots="slots"
    :text-slots="textSlots ?? {}"
    :slot-offsets="slotOffsets"
    :image-url="imageUrl"
    :image-border-radius="imageBorderRadius"
    :editable="editable"
    @slot-offset-change="(slotId, offset) => $emit('slotOffsetChange', slotId, offset)"
    @text-slot-change="(slotId, text) => $emit('textSlotChange', slotId, text)"
  />

  <div
    v-else
    class="flex h-full w-full items-center justify-center p-4 text-center"
  >
    <div class="max-w-xs space-y-2">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-400">
        Unknown layout
      </p>
      <p class="text-sm text-gray-200">
        <span class="font-mono">{{ layoutId }}</span>
      </p>
      <p class="text-xs text-gray-500">
        This page still has images saved. Add this layout to the page layout library to render it properly.
      </p>

      <div v-if="unknownSlotKeys.length" class="mt-3 grid grid-cols-2 gap-2">
        <div
          v-for="key in unknownSlotKeys"
          :key="key"
          class="overflow-hidden"
          :style="imageRadiusStyle"
        >
          <PhotobookSlotCell
            :image-path="slots[key]"
            :placeholder="key"
            dimmed
            :offset="offsetFor(key)"
            :image-url="imageUrl"
            :border-radius="imageBorderRadius"
            :editable="editable"
            @offset-change="$emit('slotOffsetChange', key, $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
