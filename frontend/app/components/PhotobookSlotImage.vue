<script setup lang="ts">
import type { SlotOffset } from '~/types/photobook'

const DEFAULT_OFFSET: SlotOffset = { x: 50, y: 50 }

const props = defineProps<{
  src: string
  alt: string
  offset?: SlotOffset
  borderRadius?: number
  editable?: boolean
}>()

const emit = defineEmits<{
  offsetChange: [offset: SlotOffset]
}>()

const containerRef = ref<HTMLElement | null>(null)
const dragging = ref(false)

const position = computed(() => props.offset ?? DEFAULT_OFFSET)

const imageStyle = computed(() => ({
  borderRadius: `${props.borderRadius ?? 0}px`,
  objectPosition: `${position.value.x}% ${position.value.y}%`,
}))

function clampPercent(value: number) {
  return Math.min(100, Math.max(0, value))
}

let dragStartX = 0
let dragStartY = 0
let startOffset: SlotOffset = { ...DEFAULT_OFFSET }

function onPointerDown(event: PointerEvent) {
  if (!props.editable || event.button !== 0) {
    return
  }
  const el = containerRef.value
  if (!el) {
    return
  }

  dragging.value = true
  dragStartX = event.clientX
  dragStartY = event.clientY
  startOffset = { ...position.value }
  el.setPointerCapture(event.pointerId)
  event.preventDefault()
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) {
    return
  }
  const el = containerRef.value
  if (!el) {
    return
  }

  const { width, height } = el.getBoundingClientRect()
  if (width <= 0 || height <= 0) {
    return
  }

  const deltaX = event.clientX - dragStartX
  const deltaY = event.clientY - dragStartY
  const panScale = 100

  emit('offsetChange', {
    x: clampPercent(startOffset.x - (deltaX / width) * panScale),
    y: clampPercent(startOffset.y - (deltaY / height) * panScale),
  })
}

function onPointerUp(event: PointerEvent) {
  if (!dragging.value) {
    return
  }
  dragging.value = false
  containerRef.value?.releasePointerCapture(event.pointerId)
}
</script>

<template>
  <div
    ref="containerRef"
    class="relative size-full overflow-hidden"
    :class="editable ? (dragging ? 'cursor-grabbing' : 'cursor-grab') : ''"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <img
      :src="src"
      :alt="alt"
      class="size-full object-cover select-none"
      :class="editable ? 'touch-none' : ''"
      :style="imageStyle"
      draggable="false"
    >
  </div>
</template>
