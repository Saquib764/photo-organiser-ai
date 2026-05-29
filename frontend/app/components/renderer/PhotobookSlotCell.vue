<script setup lang="ts">
import type { SlotOffset } from '~/types/photobook'

const props = defineProps<{
  imagePath?: string
  placeholder: string
  dimmed?: boolean
  offset?: SlotOffset
  imageUrl: (path: string) => string
  borderRadius?: number
  editable?: boolean
}>()

const emit = defineEmits<{
  offsetChange: [offset: SlotOffset]
}>()

const placeholderStyle = computed(() => ({
  borderRadius: `${props.borderRadius ?? 0}px`,
}))
</script>

<template>
  <PhotobookSlotImage
    v-if="imagePath"
    :src="imageUrl(imagePath)"
    :alt="imagePath"
    :offset="offset"
    :border-radius="borderRadius"
    :editable="editable"
    @offset-change="emit('offsetChange', $event)"
  />
  <div
    v-else
    class="flex size-full items-center justify-center text-xs text-gray-600"
    :class="dimmed ? 'bg-black/20' : ''"
    :style="placeholderStyle"
  >
    {{ placeholder }}
  </div>
</template>
