<script setup lang="ts">
defineProps<{
  percent: number
  detail: string
  color?: 'primary' | 'info' | 'secondary'
}>()
</script>

<template>
  <div class="mt-3 w-full space-y-2 border-t border-gray-800 pt-3">
    <div class="flex items-center justify-between gap-2">
      <p class="text-[10px] font-medium text-gray-300">
        Progress
      </p>
      <span class="text-[10px] tabular-nums text-gray-500">
        {{ percent }}%
      </span>
    </div>
    <UProgress
      :model-value="percent"
      :max="100"
      size="xs"
      :color="color ?? 'primary'"
    />
    <p class="text-[10px] leading-snug text-gray-500">
      {{ detail }}
    </p>
  </div>
</template>
