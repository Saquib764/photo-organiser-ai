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

const canAssign = computed(
  () => Boolean(props.focusedSlotId && props.layoutSlotIds.length),
)
</script>

<template>
  <div class="flex h-full min-h-0 flex-col border-l border-gray-800 bg-gray-900/30">
    <div class="shrink-0 border-b border-gray-800 p-4">
      <h2 class="text-xs font-bold uppercase tracking-widest text-gray-500">
        Extra images
      </h2>
      <p class="mt-1 text-xs text-gray-600">
        <template v-if="canAssign">
          Click to assign to slot “{{ focusedSlotId }}”.
        </template>
        <template v-else>
          Select a layout slot on the page to assign extras.
        </template>
      </p>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto p-3">
      <div
        v-if="!paths.length"
        class="py-8 text-center text-xs text-gray-600"
      >
        No extra images yet. Compose pages to populate alternates.
      </div>
      <div
        v-else
        class="flex flex-col gap-2"
      >
        <button
          v-for="path in paths"
          :key="path"
          type="button"
          class="group overflow-hidden rounded-lg border border-gray-800 bg-gray-900 transition hover:border-primary-500/50 disabled:cursor-default disabled:opacity-60"
          :disabled="!canAssign"
          @click="emit('assign', path)"
        >
          <img
            :src="rawUrl(path)"
            :alt="path"
            class="aspect-video w-full object-cover"
            loading="lazy"
          >
          <p class="truncate px-2 py-1 text-[10px] text-gray-600 group-hover:text-gray-400">
            {{ path.split('/').pop() }}
          </p>
        </button>
      </div>
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
