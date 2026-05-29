<script setup lang="ts">
import type { RenderNode } from '~/types/pageLayoutRender'
import type { SlotOffset, TextSlotValue } from '~/types/photobook'
import { WEDDING_THEME } from '~/utils/photobookTextSlots'

import PhotobookImageBlock from './PhotobookImageBlock.vue'
import PhotobookRenderNode from './PhotobookRenderNode.vue'
import PhotobookSlotCell from './PhotobookSlotCell.vue'
import PhotobookTextSlot from './PhotobookTextSlot.vue'

const props = defineProps<{
  node: RenderNode
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

const WEDDING_SIDE_BORDER_SVG =
  'url(\'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2212%22 height=%2248%22%3E%3Cpath d=%22M6 0c2 8-2 16 0 24s-2 16 0 24%22 fill=%22none%22 stroke=%22%239b7b67%22 stroke-width=%221%22/%3E%3C/svg%3E\')'

function offsetFor(slotId: string): SlotOffset | undefined {
  return props.slotOffsets?.[slotId]
}

function textValue(slotId: string): TextSlotValue | undefined {
  return props.textSlots[slotId]
}

function hasText(slotId: string): boolean {
  return !!textValue(slotId)?.text?.trim()
}

function onTextChange(slotId: string, text: string) {
  emit('textSlotChange', slotId, text)
}

function themeStyle(theme?: string): Record<string, string> | undefined {
  if (!theme) {
    return undefined
  }
  switch (theme) {
    case 'blush':
      return { backgroundColor: WEDDING_THEME.blush }
    case 'accentBar':
      return { backgroundColor: WEDDING_THEME.accentBar }
    case 'white':
      return { backgroundColor: WEDDING_THEME.white }
    default:
      return undefined
  }
}

const archRadius = computed(() => ({
  borderRadius: props.imageBorderRadius
    ? `${props.imageBorderRadius}px ${props.imageBorderRadius}px 0 0`
    : '50% 50% 0 0 / 45% 45% 0 0',
}))

function imageRadiusMode(mode?: string): number {
  if (mode === 'none' || mode === 'arch') {
    return 0
  }
  if (mode === 'full') {
    return 9999
  }
  return props.imageBorderRadius ?? 0
}

function showText(node: { slotId: string, when?: string }): boolean {
  if (node.when === 'always') {
    return true
  }
  return hasText(node.slotId)
}
</script>

<template>
  <!-- image -->
  <PhotobookImageBlock
    v-if="node.type === 'image'"
    :node="node"
    :slots="slots"
    :text-slots="textSlots"
    :slot-offsets="slotOffsets"
    :image-url="imageUrl"
    :image-border-radius="imageBorderRadius"
    :editable="editable"
    @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
    @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
  />

  <!-- text -->
  <PhotobookTextSlot
    v-else-if="node.type === 'text' && showText(node)"
    :slot-id="node.slotId"
    :value="textValue(node.slotId)!"
    :editable="editable"
    :multiline="node.multiline"
    :text-class="node.class"
    @text-change="onTextChange"
  />

  <!-- divider -->
  <div
    v-else-if="node.type === 'divider'"
    :class="node.class ?? 'mx-auto h-px w-16 bg-[#9b7b67]/40'"
  />

  <!-- ornament -->
  <template v-else-if="node.type === 'ornament'">
    <template v-if="node.variant === 'wedding_side_borders'">
      <div
        class="pointer-events-none absolute inset-y-4 left-2 w-3 bg-repeat-y opacity-90"
        :style="{ backgroundImage: WEDDING_SIDE_BORDER_SVG }"
      />
      <div
        class="pointer-events-none absolute inset-y-4 right-2 w-3 bg-repeat-y opacity-90"
        :style="{ backgroundImage: WEDDING_SIDE_BORDER_SVG }"
      />
    </template>
    <div
      v-else-if="node.variant === 'accent_bar'"
      class="relative z-10 mt-3 h-6 shrink-0"
      :style="{ backgroundColor: WEDDING_THEME.accentBar }"
    />
    <div
      v-else-if="node.variant === 'arch_caption_well'"
      class="mx-auto mt-4 flex min-h-0 w-[78%] flex-1 flex-col items-center justify-center rounded-t-[50%] bg-white px-5 py-6 shadow-sm"
      style="border-radius: 50% 50% 0 0 / 35% 35% 0 0"
    >
      <slot />
    </div>
    <div
      v-else-if="node.variant === 'hairline'"
      class="mx-auto h-px w-16 bg-[#9b7b67]/40"
    />
  </template>

  <!-- box -->
  <div
    v-else-if="node.type === 'box'"
    :class="node.class"
    :style="{ ...themeStyle(node.themeBackground), ...node.style, flex: node.flex }"
  >
    <div
      v-if="node.imageFrame === 'arch'"
      class="h-full w-full overflow-hidden"
      :style="archRadius"
    >
      <PhotobookRenderNode
        v-for="(child, index) in node.children ?? []"
        :key="index"
        :node="child"
        :slots="slots"
        :text-slots="textSlots"
        :slot-offsets="slotOffsets"
        :image-url="imageUrl"
        :image-border-radius="imageBorderRadius"
        :editable="editable"
        @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
        @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
      />
    </div>
    <template v-else>
      <PhotobookRenderNode
        v-for="(child, index) in node.children ?? []"
        :key="index"
        :node="child"
        :slots="slots"
        :text-slots="textSlots"
        :slot-offsets="slotOffsets"
        :image-url="imageUrl"
        :image-border-radius="imageBorderRadius"
        :editable="editable"
        @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
        @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
      />
    </template>
  </div>

  <!-- stack -->
  <div
    v-else-if="node.type === 'stack'"
    :class="node.class"
    :style="{
      ...themeStyle(node.themeBackground),
      display: 'flex',
      flexDirection: node.direction === 'row' ? 'row' : 'column',
      gap: typeof node.gap === 'number' ? `${node.gap}px` : node.gap,
    }"
  >
    <PhotobookRenderNode
      v-for="(child, index) in node.children"
      :key="index"
      :node="child"
      :slots="slots"
      :text-slots="textSlots"
      :slot-offsets="slotOffsets"
      :image-url="imageUrl"
      :image-border-radius="imageBorderRadius"
      :editable="editable"
      @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
      @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
    />
  </div>

  <!-- grid -->
  <div
    v-else-if="node.type === 'grid'"
    :class="node.class"
    :style="{
      display: 'grid',
      gridTemplateColumns: node.templateColumns ?? (node.cols ? `repeat(${node.cols}, 1fr)` : undefined),
      gridTemplateRows: node.templateRows,
      gap: typeof node.gap === 'number' ? `${node.gap}px` : node.gap,
    }"
  >
    <PhotobookRenderNode
      v-for="(child, index) in node.children"
      :key="index"
      :node="child"
      :slots="slots"
      :text-slots="textSlots"
      :slot-offsets="slotOffsets"
      :image-url="imageUrl"
      :image-border-radius="imageBorderRadius"
      :editable="editable"
      @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
      @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
    />
  </div>

  <!-- absolute -->
  <div
    v-else-if="node.type === 'absolute'"
    :class="node.class"
  >
    <PhotobookRenderNode
      v-for="(child, index) in node.children"
      :key="index"
      :node="child"
      :slots="slots"
      :text-slots="textSlots"
      :slot-offsets="slotOffsets"
      :image-url="imageUrl"
      :image-border-radius="imageBorderRadius"
      :editable="editable"
      @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
      @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
    />
  </div>

  <!-- foreach -->
  <template v-else-if="node.type === 'foreach'">
    <div
      v-for="key in node.keys"
      :key="key"
      :class="node.class"
    >
      <PhotobookRenderNode
        :node="{
          ...node.child,
          ...(node.child.type === 'image' ? { slotId: key, placeholder: key } : {}),
        }"
        :slots="slots"
        :text-slots="textSlots"
        :slot-offsets="slotOffsets"
        :image-url="imageUrl"
        :image-border-radius="imageBorderRadius"
        :editable="editable"
        @slot-offset-change="(id, o) => emit('slotOffsetChange', id, o)"
        @text-slot-change="(id, t) => emit('textSlotChange', id, t)"
      />
    </div>
  </template>

  <!-- mosaic -->
  <div
    v-else-if="node.type === 'mosaic'"
    :class="node.class"
    :style="{
      display: 'grid',
      gridTemplateColumns: node.templateColumns,
      gridTemplateRows: node.templateRows,
      gap: node.gap,
    }"
  >
    <div
      v-for="cell in node.cells"
      :key="cell.slotId"
      class="min-h-0 overflow-hidden"
      :style="{ gridColumn: cell.gridColumn }"
    >
      <PhotobookSlotCell
        :image-path="slots[cell.slotId]"
        :placeholder="cell.slotId"
        dimmed
        :offset="offsetFor(cell.slotId)"
        :image-url="imageUrl"
        :border-radius="imageBorderRadius"
        :editable="editable"
        @offset-change="emit('slotOffsetChange', cell.slotId, $event)"
      />
    </div>
  </div>
</template>
