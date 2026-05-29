<script setup lang="ts">
import type { TextSlotValue } from '~/types/photobook'
import { textSlotStyle } from '~/utils/photobookTextSlots'

const props = withDefaults(
  defineProps<{
    slotId: string
    value: TextSlotValue
    editable?: boolean
    textClass?: string
    multiline?: boolean
  }>(),
  {
    editable: false,
    multiline: false,
  },
)

const emit = defineEmits<{
  textChange: [slotId: string, text: string]
}>()

const root = ref<HTMLElement | null>(null)
const isFocused = ref(false)

const style = computed(() => textSlotStyle(props.value))

const placeholder = computed(() =>
  props.multiline ? 'Click to add text…' : 'Click to edit',
)

function syncDomText() {
  const el = root.value
  if (!el || isFocused.value) {
    return
  }
  el.textContent = props.value.text || ''
}

watch(() => props.value.text, syncDomText)

onMounted(syncDomText)

function commitText() {
  const el = root.value
  if (!el) {
    return
  }
  const next = el.textContent?.replace(/\u00a0/g, ' ').trim() ?? ''
  if (next !== props.value.text) {
    emit('textChange', props.slotId, next)
  }
}

function onBlur() {
  isFocused.value = false
  commitText()
}

function onFocus() {
  if (!props.editable) {
    return
  }
  isFocused.value = true
}

function onInput() {
  if (!props.multiline && root.value) {
    const text = root.value.textContent ?? ''
    if (text.includes('\n')) {
      root.value.textContent = text.replace(/\n/g, ' ')
    }
  }
}

function onKeydown(event: KeyboardEvent) {
  if (!props.editable) {
    return
  }
  if (event.key === 'Enter' && !props.multiline) {
    event.preventDefault()
    root.value?.blur()
  }
  if (event.key === 'Escape') {
    event.preventDefault()
    if (root.value) {
      root.value.textContent = props.value.text || ''
    }
    root.value?.blur()
  }
}
</script>

<template>
  <component
    :is="multiline ? 'div' : 'p'"
    ref="root"
    role="textbox"
    :aria-label="`Edit ${slotId} text`"
    :contenteditable="editable"
    suppress-contenteditable-warning
    :data-placeholder="placeholder"
    :class="[
      textClass,
      'photobook-text-slot bg-transparent outline-none',
      multiline ? 'min-h-[1.25em] whitespace-pre-wrap' : 'whitespace-pre-wrap',
      editable && 'cursor-text hover:outline hover:outline-1 hover:outline-primary-400/40 focus:outline focus:outline-2 focus:outline-primary-400/60',
      editable && !value.text && 'photobook-text-slot--empty',
    ]"
    :style="style"
    @focus="onFocus"
    @blur="onBlur"
    @input="onInput"
    @keydown="onKeydown"
  />
</template>

<style scoped>
.photobook-text-slot {
  background-color: transparent;
}

.photobook-text-slot--empty:empty::before {
  content: attr(data-placeholder);
  opacity: 0.35;
  pointer-events: none;
}
</style>
