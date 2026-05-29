<script setup lang="ts">
const {
  imageSummary,
  imageSummaryShort,
  analysisSummary,
  connectionLabel,
  connectionColor,
  connectionDotClass,
  connectionState,
  requestStatus,
} = useWorkspaceStatusDisplay()

const { aspectRatio, aspectItems } = usePhotobookUiPrefs()
</script>

<template>
  <header
    class="flex min-h-16 shrink-0 items-center gap-4 border-b border-gray-800 bg-gray-900 px-4 py-3 lg:px-6"
  >
    <NuxtLink
      to="/"
      class="group flex min-w-0 items-center gap-2.5"
    >
      <div
        class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary-500/10 ring-1 ring-primary-500/30"
      >
        <UIcon
          name="i-heroicons-photo"
          class="size-6 text-primary-400"
        />
      </div>
      <div class="min-w-0">
        <h1 class="tf-page-title truncate transition-colors group-hover:text-primary-400">
          Organise photos into albums
        </h1>
        <p class="tf-section-subtitle hidden truncate sm:block">
          Turn scattered photos into curated albums with AI.
        </p>
      </div>
    </NuxtLink>

    <div class="flex-1" />

    <div class="flex shrink-0 items-center gap-3 sm:gap-4">
      <USelect
        v-model="aspectRatio"
        :items="aspectItems"
        value-key="value"
        label-key="label"
        size="sm"
        color="neutral"
        variant="outline"
        class="w-[92px]"
        :ui="{ base: 'text-xs' }"
        title="Photobook aspect ratio"
      />

      <div
        v-if="analysisSummary"
        class="hidden items-center gap-1.5 text-gray-400 md:flex"
        :title="analysisSummary"
      >
        <UIcon
          name="i-heroicons-sparkles"
          class="size-4 shrink-0 text-gray-500"
          aria-hidden="true"
        />
        <span class="text-sm tabular-nums text-gray-300">
          {{ analysisSummary }}
        </span>
      </div>

      <div
        class="flex items-center gap-1.5 text-gray-400"
        :title="imageSummary ?? 'Waiting for library status'"
      >
        <UIcon
          name="i-heroicons-photo"
          class="size-4 shrink-0 text-gray-500"
          aria-hidden="true"
        />
        <span class="hidden text-sm tabular-nums text-gray-300 sm:inline">
          <template v-if="imageSummary">
            {{ imageSummary }}
          </template>
          <template v-else-if="connectionState === 'open'">
            No images yet
          </template>
          <template v-else>
            —
          </template>
        </span>
        <span class="text-xs font-medium tabular-nums text-gray-400 sm:hidden">
          {{ imageSummaryShort }}
        </span>
      </div>

      <div class="flex shrink-0 items-center gap-1">
        <UButton
          icon="i-heroicons-arrow-path"
          size="sm"
          color="neutral"
          variant="ghost"
          aria-label="Refresh status"
          title="Refresh library status"
          :disabled="connectionState !== 'open'"
          @click="requestStatus({ discover: true })"
        />
        <UBadge
          :color="connectionColor"
          variant="subtle"
          size="sm"
          class="shrink-0"
          :label="connectionLabel"
        >
          <template #leading>
            <span
              class="size-1.5 shrink-0 rounded-full"
              :class="connectionDotClass"
              aria-hidden="true"
            />
          </template>
        </UBadge>
      </div>
    </div>
  </header>
</template>
