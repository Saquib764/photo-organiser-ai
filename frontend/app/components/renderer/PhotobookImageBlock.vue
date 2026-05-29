<script setup lang="ts">
import type { RenderImageNode } from '~/types/pageLayoutRender'
import type { SlotOffset, TextSlotValue } from '~/types/photobook'
import { overlayPositionClasses, overlayTextPillClass } from '~/utils/overlayPosition'

import PhotobookSlotCell from './PhotobookSlotCell.vue'
import PhotobookTextSlot from './PhotobookTextSlot.vue'

const props = defineProps<{
  node: RenderImageNode
  slots: Record<string, string>
  textSlots: Record<string, TextSlotValue>
  slotOffsets?: Record<string, SlotOffset>
  imageUrl: (path: string) => string
  imageBorderRadius?: number
  editable?: boolean
}>()

const emit = defineEmits<{
  slotOffsetChange: [slotId: string, offset: SlotOffset]
  textSlotChange: [slotId: string, text: string]
}>()

function offsetFor(slotId: string): SlotOffset | undefined {
  return props.slotOffsets?.[slotId]
}

function textValue(slotId: string): TextSlotValue | undefined {
  return props.textSlots[slotId]
}

function showOverlayContent(): boolean {
  const overlay = props.node.overlay
  if (!overlay) {
    return false
  }
  const value = textValue(overlay.textSlotId)
  if (!value) {
    return false
  }
  if (overlay.when === 'always') {
    return true
  }
  return !!value.text
}

function showOverlayLayer(): boolean {
  if (!props.node.overlay || !overlayValue.value) {
    return false
  }
  if (props.editable) {
    return true
  }
  return showOverlayContent()
}

function imageRadiusMode(mode?: string): number {
  if (mode === 'none' || mode === 'arch') {
    return 0
  }
  if (mode === 'full') {
    return 9999
  }
  return props.imageBorderRadius ?? 0
}

const overlay = computed(() => props.node.overlay)
const overlayValue = computed(() =>
  overlay.value ? textValue(overlay.value.textSlotId) : undefined,
)
</script>

<template>
  <div class="relative size-full min-h-0 overflow-hidden">
    <PhotobookSlotCell
      :image-path="slots[node.slotId]"
      :placeholder="node.placeholder ?? node.slotId"
      :dimmed="node.dimmed"
      :offset="offsetFor(node.slotId)"
      :image-url="imageUrl"
      :border-radius="imageRadiusMode(node.borderRadius)"
      :editable="editable"
      @offset-change="emit('slotOffsetChange', node.slotId, $event)"
    />
    <template v-if="overlay && overlayValue && showOverlayLayer()">
      <div
        class="pointer-events-none absolute inset-0"
        :class="overlayPositionClasses(overlay.x, overlay.y)"
      >
        <div
          class="pointer-events-auto w-fit max-w-full"
          :class="overlayTextPillClass"
        >
          <PhotobookTextSlot
            :slot-id="overlay.textSlotId"
            :value="overlayValue"
            :editable="editable"
            :text-class="[
              overlay.class ?? 'text-center',
            ]"
            @text-change="(id, text) => emit('textSlotChange', id, text)"
          />
        </div>
      </div>
    </template>
  </div>
</template>
