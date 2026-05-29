<script setup lang="ts">
type FlagRow = {
  key: string
  label: string
  description: string
  active: boolean
  isResize?: boolean
  isPalette?: boolean
  isAnalysis?: boolean
  isCategorisation?: boolean
}

const {
  flags,
  isResizePhase,
  isPalettePhase,
  isAnalysisPhase,
  isCategorisationPhase,
  showResizeProgress,
  showPaletteProgress,
  showAnalysisProgress,
  showCategorisationProgress,
  progressPercent,
  resizeCountText,
  resizeTotalCount,
  paletteCountText,
  paletteTotalCount,
  analysisCountText,
  analysisTotalCount,
  categorisationCountText,
  categorisationTotalCount,
  resizeProgressDetailText,
  paletteProgressDetailText,
  analysisProgressDetailText,
  categorisationProgressDetailText,
  canStartProcessing,
  canStartPalette,
  showAnalysisActions,
  showAnalysisOpenAiHint,
  showStartAnalysis,
  showResumeAnalysis,
  showRerunAnalysis,
  showCategorisationActions,
  showCategorisationOpenAiHint,
  showStartCategorisation,
  showResumeCategorisation,
  showRerunCategorisation,
  processingBusy,
  actionsDisabled,
  openSettingsTab,
  startProcessing,
  startPaletteExtraction,
  startAnalysis,
  rerunAnalysis,
  startCategorisation,
  rerunCategorisation,
} = useWorkspaceStatusDisplay()

const analysisButtons = computed(() => {
  const buttons: Array<{
    label: string
    icon: string
    color: 'primary' | 'neutral'
    variant: 'solid' | 'outline'
    onClick: () => void
  }> = []

  if (showStartAnalysis.value) {
    buttons.push({
      label: 'Start',
      icon: 'i-heroicons-sparkles',
      color: 'primary',
      variant: 'solid',
      onClick: startAnalysis,
    })
  }
  if (showResumeAnalysis.value) {
    buttons.push({
      label: 'Resume',
      icon: 'i-heroicons-play',
      color: 'primary',
      variant: 'solid',
      onClick: startAnalysis,
    })
  }
  if (showRerunAnalysis.value) {
    buttons.push({
      label: 'Rerun',
      icon: 'i-heroicons-arrow-path',
      color: 'neutral',
      variant: 'outline',
      onClick: rerunAnalysis,
    })
  }

  return buttons
})

const categorisationButtons = computed(() => {
  const buttons: Array<{
    label: string
    icon: string
    color: 'primary' | 'neutral'
    variant: 'solid' | 'outline'
    onClick: () => void
  }> = []

  if (showStartCategorisation.value) {
    buttons.push({
      label: 'Start',
      icon: 'i-heroicons-squares-2x2',
      color: 'primary',
      variant: 'solid',
      onClick: startCategorisation,
    })
  }
  if (showResumeCategorisation.value) {
    buttons.push({
      label: 'Resume',
      icon: 'i-heroicons-play',
      color: 'primary',
      variant: 'solid',
      onClick: startCategorisation,
    })
  }
  if (showRerunCategorisation.value) {
    buttons.push({
      label: 'Rerun',
      icon: 'i-heroicons-arrow-path',
      color: 'neutral',
      variant: 'outline',
      onClick: rerunCategorisation,
    })
  }

  return buttons
})

function flagIcon(row: FlagRow) {
  if (row.key === 'resize_complete' && isResizePhase.value) {
    return { name: 'i-heroicons-arrow-path', class: 'text-amber-400 animate-spin' }
  }
  if (row.key === 'has_analysed_color' && isPalettePhase.value) {
    return { name: 'i-heroicons-swatch', class: 'text-violet-400 animate-spin' }
  }
  if (row.key === 'has_analysed_color') {
    return {
      name: row.active ? 'i-heroicons-swatch' : 'i-heroicons-minus-circle',
      class: row.active ? 'text-violet-400' : 'text-gray-600',
    }
  }
  if (row.key === 'categorisation_complete' && isCategorisationPhase.value) {
    return { name: 'i-heroicons-squares-2x2', class: 'text-emerald-400 animate-spin' }
  }
  return {
    name: row.active ? 'i-heroicons-check-circle' : 'i-heroicons-minus-circle',
    class: row.active ? 'text-primary-400' : 'text-gray-600',
  }
}

const flagRows = computed<FlagRow[]>(() => [
  {
    key: 'image_found',
    label: 'Photos added',
    description: 'At least one image is present in your library',
    active: flags.value.image_found,
  },
  {
    key: 'resize_complete',
    label: isResizePhase.value ? 'Creating thumbnails' : 'Thumbnails',
    description: isResizePhase.value
      ? 'Building smaller copies for fast browsing and AI steps'
      : 'Every original has a matching file in processed_small',
    active: flags.value.resize_complete,
    isResize: true,
  },
  {
    key: 'has_analysed_color',
    label: isPalettePhase.value ? 'Extracting colours' : 'Colours',
    description: isPalettePhase.value
      ? 'Saving dominant colour palettes per image'
      : 'Colour palettes saved for every thumbnail',
    active: flags.value.has_analysed_color,
    isPalette: true,
  },
  {
    key: 'image_analysis_complete',
    label: isAnalysisPhase.value ? 'Writing captions' : 'Captions',
    description: isAnalysisPhase.value
      ? 'Generating descriptions and people metadata with AI'
      : 'Every thumbnail has an AI caption and quality score',
    active: flags.value.image_analysis_complete,
    isAnalysis: true,
  },
  {
    key: 'categorisation_complete',
    label: isCategorisationPhase.value ? 'Grouping photos' : 'Categories',
    description: isCategorisationPhase.value
      ? 'Sorting images into story categories for photobook planning'
      : 'Every captioned photo is assigned to a story category',
    active: flags.value.categorisation_complete,
    isCategorisation: true,
  },
])
</script>

<template>
  <ul class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5 sm:gap-3">
    <li
      v-for="row in flagRows"
      :key="row.key"
      class="tf-card flex h-full flex-col !p-3 sm:!p-4"
    >
      <div class="flex items-start gap-2.5">
        <UIcon
          :name="flagIcon(row).name"
          class="mt-0.5 size-5 shrink-0"
          :class="flagIcon(row).class"
        />
        <div class="min-w-0 flex-1">
          <p class="text-xs font-medium leading-snug text-gray-200 sm:text-sm">
            {{ row.label }}
          </p>
          <p
            v-if="row.isAnalysis && showAnalysisOpenAiHint"
            class="mt-1 text-xs leading-snug text-amber-200/90"
          >
            Caption analysis needs an OpenAI API key.
            <button
              type="button"
              class="text-primary-400 underline decoration-primary-400/40 underline-offset-2 hover:text-primary-300"
              @click="openSettingsTab"
            >
              Settings
            </button>.
          </p>
          <p
            v-else-if="row.isCategorisation && showCategorisationOpenAiHint"
            class="mt-1 text-xs leading-snug text-amber-200/90"
          >
            Categorising photos needs an OpenAI API key.
            <button
              type="button"
              class="text-primary-400 underline decoration-primary-400/40 underline-offset-2 hover:text-primary-300"
              @click="openSettingsTab"
            >
              Settings
            </button>.
          </p>
          <p
            v-else
            class="mt-1 text-xs leading-snug text-gray-500"
            :class="(row.isResize && showResizeProgress) || (row.isPalette && showPaletteProgress) || (row.isAnalysis && showAnalysisProgress) || (row.isCategorisation && showCategorisationProgress) ? 'hidden sm:block' : ''"
          >
            {{ row.description }}
          </p>
        </div>
      </div>

      <LibraryFlagCardProgress
        v-if="row.isResize && showResizeProgress"
        :percent="progressPercent"
        :detail="resizeProgressDetailText"
      />

      <div
        v-else-if="row.isResize && canStartProcessing"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <UButton
          size="xs"
          color="primary"
          variant="solid"
          icon="i-heroicons-play"
          :label="flags.resize_complete ? 'Run again' : 'Start'"
          :disabled="actionsDisabled"
          @click="startProcessing"
        />
        <p
          v-if="resizeTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ resizeCountText }}
        </p>
      </div>

      <LibraryFlagCardProgress
        v-if="row.isPalette && showPaletteProgress"
        :percent="progressPercent"
        :detail="paletteProgressDetailText"
        color="secondary"
      />

      <div
        v-else-if="row.isPalette && canStartPalette"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <UButton
          size="xs"
          color="secondary"
          variant="solid"
          icon="i-heroicons-play"
          :label="flags.has_analysed_color ? 'Run again' : 'Start'"
          :disabled="actionsDisabled"
          @click="startPaletteExtraction"
        />
        <p
          v-if="paletteTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ paletteCountText }}
        </p>
      </div>

      <LibraryFlagCardProgress
        v-if="row.isAnalysis && showAnalysisProgress"
        :percent="progressPercent"
        :detail="analysisProgressDetailText"
        color="info"
      />

      <div
        v-else-if="row.isAnalysis && showAnalysisActions"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <div class="flex min-w-0 flex-wrap gap-1">
          <UButton
            v-for="button in analysisButtons"
            :key="button.label"
            size="xs"
            :color="button.color"
            :variant="button.variant"
            :icon="button.icon"
            :label="button.label"
            :disabled="actionsDisabled"
            @click="button.onClick"
          />
        </div>
        <p
          v-if="analysisTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ analysisCountText }}
        </p>
      </div>

      <div
        v-else-if="row.isAnalysis && showAnalysisOpenAiHint"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <UButton
          size="xs"
          color="primary"
          variant="outline"
          icon="i-heroicons-cog-6-tooth"
          label="Settings"
          @click="openSettingsTab"
        />
        <p
          v-if="analysisTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ analysisCountText }}
        </p>
      </div>

      <LibraryFlagCardProgress
        v-if="row.isCategorisation && showCategorisationProgress"
        :percent="progressPercent"
        :detail="categorisationProgressDetailText"
        color="success"
      />

      <div
        v-else-if="row.isCategorisation && showCategorisationActions"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <div class="flex min-w-0 flex-wrap gap-1">
          <UButton
            v-for="button in categorisationButtons"
            :key="button.label"
            size="xs"
            :color="button.color"
            :variant="button.variant"
            :icon="button.icon"
            :label="button.label"
            :disabled="actionsDisabled"
            @click="button.onClick"
          />
        </div>
        <p
          v-if="categorisationTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ categorisationCountText }}
        </p>
      </div>

      <div
        v-else-if="row.isCategorisation && showCategorisationOpenAiHint"
        class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-800 pt-3"
      >
        <UButton
          size="xs"
          color="primary"
          variant="outline"
          icon="i-heroicons-cog-6-tooth"
          label="Settings"
          @click="openSettingsTab"
        />
        <p
          v-if="categorisationTotalCount > 0"
          class="shrink-0 text-xs tabular-nums leading-snug text-gray-400"
        >
          {{ categorisationCountText }}
        </p>
      </div>
    </li>
  </ul>
</template>
