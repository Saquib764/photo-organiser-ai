import type { WorkspaceConnectionState } from '~/composables/useWorkspaceSocket'
import type { LibraryFlags } from '~/types/workspace'

const EMPTY_FLAGS: LibraryFlags = {
  image_found: false,
  resize_complete: false,
  people_extraction_complete: false,
  has_analysed_color: false,
  image_analysis_complete: false,
  categorisation_complete: false,
}

export function useWorkspaceStatusDisplay() {
  const {
    status,
    connectionState,
    requestStatus,
    startProcessing,
    startPaletteExtraction,
    startFaceExtraction,
    rerunFaceExtraction,
    startAnalysis,
    rerunAnalysis,
    startCategorisation,
    rerunCategorisation,
  } = useWorkspaceSocket()

  const flags = computed(() => status.value?.flags ?? EMPTY_FLAGS)

  const connectionLabel = computed(() => {
    switch (connectionState.value) {
      case 'open':
        return 'Connected'
      case 'connecting':
        return 'Connecting'
      default:
        return 'Disconnected'
    }
  })

  const connectionColor = computed(() => {
    switch (connectionState.value) {
      case 'open':
        return 'success' as const
      case 'connecting':
        return 'warning' as const
      default:
        return 'neutral' as const
    }
  })

  const connectionDotClass = computed(() => {
    const map: Record<WorkspaceConnectionState, string> = {
      open: 'bg-emerald-400',
      connecting: 'bg-amber-400 animate-pulse',
      closed: 'bg-gray-600',
    }
    return map[connectionState.value]
  })

  const totalImages = computed(() => {
    if (!status.value) {
      return null
    }
    return status.value.total_images_raw
  })

  const imageSummary = computed(() => {
    if (totalImages.value === null) {
      return null
    }
    const n = totalImages.value
    return `${n.toLocaleString()} ${n === 1 ? 'image' : 'images'}`
  })

  const imageSummaryShort = computed(() => {
    if (totalImages.value === null) {
      return '—'
    }
    return totalImages.value.toLocaleString()
  })

  const processingBusy = computed(() => status.value?.processing_busy ?? false)
  const processingPhase = computed(() => status.value?.processing_phase ?? null)

  const actionsDisabled = computed(
    () => connectionState.value !== 'open' || processingBusy.value,
  )

  const canStartProcessing = computed(
    () => flags.value.image_found && !processingBusy.value,
  )

  const canStartPalette = computed(
    () => flags.value.resize_complete && !processingBusy.value,
  )

  const canStartFaceExtraction = computed(
    () => flags.value.resize_complete && !processingBusy.value,
  )

  const isFacePhase = computed(
    () => processingPhase.value === 'faces',
  )

  const isPalettePhase = computed(
    () => processingPhase.value === 'palette',
  )

  const isAnalysisPhase = computed(
    () => processingPhase.value === 'analysis',
  )

  const isCategorisationPhase = computed(
    () => processingPhase.value === 'categorise',
  )

  const isResizePhase = computed(
    () => processingPhase.value === 'resize',
  )

  const progressTotal = computed(() => status.value?.progress_total ?? 0)
  const progressCompleted = computed(() => status.value?.progress_completed ?? 0)
  const progressRemaining = computed(() => status.value?.progress_remaining ?? 0)

  function formatImageCount(exists: number, total: number) {
    return `${exists.toLocaleString()}/${total.toLocaleString()} images`
  }

  const resizeCompletedCount = computed(
    () => status.value?.resize_completed_count ?? 0,
  )
  const resizeTotalCount = computed(() => status.value?.resize_total_count ?? 0)
  const paletteCompletedCount = computed(
    () => status.value?.palette_completed_count ?? 0,
  )
  const paletteTotalCount = computed(() => status.value?.palette_total_count ?? 0)
  const faceCompletedCount = computed(
    () => status.value?.face_completed_count ?? 0,
  )
  const faceTotalCount = computed(() => status.value?.face_total_count ?? 0)
  const personsCount = computed(() => status.value?.persons_count ?? 0)
  const analysisCompletedCount = computed(
    () => status.value?.analysis_completed_count ?? 0,
  )
  const analysisTotalCount = computed(
    () => status.value?.analysis_total_count ?? 0,
  )
  const categorisationCompletedCount = computed(
    () => status.value?.categorisation_completed_count ?? 0,
  )
  const categorisationTotalCount = computed(
    () => status.value?.categorisation_total_count ?? 0,
  )

  function stepProgressPercent(completed: number, total: number) {
    if (total === 0) {
      return 0
    }
    return Math.round((completed / total) * 100)
  }

  const progressPercent = computed(() => {
    if (isResizePhase.value) {
      return stepProgressPercent(resizeCompletedCount.value, resizeTotalCount.value)
    }
    if (isFacePhase.value) {
      return stepProgressPercent(faceCompletedCount.value, faceTotalCount.value)
    }
    if (isPalettePhase.value) {
      return stepProgressPercent(paletteCompletedCount.value, paletteTotalCount.value)
    }
    if (isAnalysisPhase.value) {
      return stepProgressPercent(
        analysisCompletedCount.value,
        analysisTotalCount.value,
      )
    }
    if (isCategorisationPhase.value) {
      return stepProgressPercent(
        categorisationCompletedCount.value,
        categorisationTotalCount.value,
      )
    }
    return stepProgressPercent(progressCompleted.value, progressTotal.value)
  })

  const showResizeProgress = computed(
    () =>
      isResizePhase.value
      && processingBusy.value
      && resizeTotalCount.value > 0,
  )

  const showFaceProgress = computed(
    () =>
      isFacePhase.value
      && processingBusy.value
      && faceTotalCount.value > 0,
  )

  const showPaletteProgress = computed(
    () =>
      isPalettePhase.value
      && processingBusy.value
      && paletteTotalCount.value > 0,
  )

  const showAnalysisProgress = computed(
    () =>
      isAnalysisPhase.value
      && processingBusy.value
      && analysisTotalCount.value > 0,
  )

  const showCategorisationProgress = computed(
    () =>
      isCategorisationPhase.value
      && processingBusy.value
      && categorisationTotalCount.value > 0,
  )

  const resizeCountText = computed(() =>
    formatImageCount(resizeCompletedCount.value, resizeTotalCount.value),
  )

  const faceCountText = computed(() =>
    formatImageCount(faceCompletedCount.value, faceTotalCount.value),
  )

  const personsCountText = computed(() => {
    const n = personsCount.value
    if (n === 0) {
      return null
    }
    return `${n.toLocaleString()} ${n === 1 ? 'person' : 'people'}`
  })

  const paletteCountText = computed(() =>
    formatImageCount(paletteCompletedCount.value, paletteTotalCount.value),
  )

  const analysisCountText = computed(() =>
    formatImageCount(analysisCompletedCount.value, analysisTotalCount.value),
  )

  const categorisationCountText = computed(() =>
    formatImageCount(
      categorisationCompletedCount.value,
      categorisationTotalCount.value,
    ),
  )

  const resizeProgressDetailText = resizeCountText
  const faceProgressDetailText = faceCountText
  const paletteProgressDetailText = paletteCountText
  const analysisProgressDetailText = analysisCountText
  const categorisationProgressDetailText = categorisationCountText

  const analysisSummary = computed(() => {
    if (analysisTotalCount.value === 0) {
      return null
    }
    return analysisCountText.value
  })

  const openaiConfigured = computed(
    () => status.value?.openai_configured ?? false,
  )

  const captionsAvailable = computed(
    () => analysisCompletedCount.value > 0,
  )

  const categoriesAvailable = computed(
    () => (status.value?.categories_count ?? 0) > 0,
  )

  const peopleAvailable = computed(
    () => flags.value.people_extraction_complete,
  )

  const showStartFaceExtraction = computed(
    () =>
      canStartFaceExtraction.value
      && !processingBusy.value
      && faceCompletedCount.value === 0,
  )

  const showResumeFaceExtraction = computed(
    () =>
      canStartFaceExtraction.value
      && !processingBusy.value
      && faceCompletedCount.value > 0
      && faceCompletedCount.value < faceTotalCount.value,
  )

  const showRerunFaceExtraction = computed(
    () =>
      canStartFaceExtraction.value
      && !processingBusy.value
      && faceCompletedCount.value > 0,
  )

  const showFaceExtractionActions = computed(
    () =>
      canStartFaceExtraction.value
      && !processingBusy.value
      && (
        showStartFaceExtraction.value
        || showResumeFaceExtraction.value
        || showRerunFaceExtraction.value
      ),
  )

  const analysisPrerequisitesMet = computed(
    () =>
      flags.value.resize_complete
      && flags.value.has_analysed_color
      && analysisTotalCount.value > 0,
  )

  const analysisActionsAvailable = computed(
    () => analysisPrerequisitesMet.value && openaiConfigured.value,
  )

  const showAnalysisOpenAiHint = computed(
    () =>
      !openaiConfigured.value
      && !processingBusy.value
      && !isAnalysisPhase.value,
  )

  const documentActiveTab = useState('document-active-tab', () => 'library')

  function openSettingsTab() {
    documentActiveTab.value = 'settings'
  }

  const showStartAnalysis = computed(
    () =>
      analysisActionsAvailable.value
      && !processingBusy.value
      && analysisCompletedCount.value === 0,
  )

  const showResumeAnalysis = computed(
    () =>
      analysisActionsAvailable.value
      && !processingBusy.value
      && analysisCompletedCount.value > 0
      && analysisCompletedCount.value < analysisTotalCount.value,
  )

  const showRerunAnalysis = computed(
    () =>
      analysisActionsAvailable.value
      && !processingBusy.value
      && analysisCompletedCount.value > 0,
  )

  const showAnalysisActions = computed(
    () =>
      analysisActionsAvailable.value
      && !processingBusy.value
      && (showStartAnalysis.value || showResumeAnalysis.value || showRerunAnalysis.value),
  )

  const categorisationPrerequisitesMet = computed(
    () =>
      flags.value.image_analysis_complete
      && categorisationTotalCount.value > 0,
  )

  const categorisationActionsAvailable = computed(
    () => categorisationPrerequisitesMet.value && openaiConfigured.value,
  )

  const showCategorisationOpenAiHint = computed(
    () =>
      flags.value.image_analysis_complete
      && !openaiConfigured.value
      && !processingBusy.value
      && !isCategorisationPhase.value,
  )

  const showStartCategorisation = computed(
    () =>
      categorisationActionsAvailable.value
      && !processingBusy.value
      && categorisationCompletedCount.value === 0,
  )

  const showResumeCategorisation = computed(
    () =>
      categorisationActionsAvailable.value
      && !processingBusy.value
      && categorisationCompletedCount.value > 0
      && categorisationCompletedCount.value < categorisationTotalCount.value,
  )

  const showRerunCategorisation = computed(
    () =>
      categorisationActionsAvailable.value
      && !processingBusy.value
      && categorisationCompletedCount.value > 0,
  )

  const showCategorisationActions = computed(
    () =>
      categorisationActionsAvailable.value
      && !processingBusy.value
      && (
        showStartCategorisation.value
        || showResumeCategorisation.value
        || showRerunCategorisation.value
      ),
  )

  const STATUS_POLL_DELAY_MS = 4000
  let statusPollGeneration = 0

  function delay(ms: number) {
    return new Promise<void>((resolve) => {
      setTimeout(resolve, ms)
    })
  }

  function stopStatusPoll() {
    statusPollGeneration += 1
  }

  async function runStatusPollLoop(generation: number) {
    while (generation === statusPollGeneration) {
      if (!processingBusy.value || connectionState.value !== 'open') {
        return
      }

      await requestStatus()

      if (generation !== statusPollGeneration || !processingBusy.value) {
        return
      }

      await delay(STATUS_POLL_DELAY_MS)
    }
  }

  function startStatusPoll() {
    if (!import.meta.client) {
      return
    }
    const generation = statusPollGeneration
    void runStatusPollLoop(generation)
  }

  watch(processingBusy, (busy) => {
    if (busy) {
      startStatusPoll()
    }
    else {
      stopStatusPoll()
    }
  }, { immediate: true })

  onScopeDispose(() => {
    stopStatusPoll()
  })

  return {
    status,
    flags,
    connectionState,
    connectionLabel,
    connectionColor,
    connectionDotClass,
    totalImages,
    imageSummary,
    imageSummaryShort,
    processingBusy,
    processingPhase,
    actionsDisabled,
    canStartProcessing,
    canStartPalette,
    canStartFaceExtraction,
    isFacePhase,
    isPalettePhase,
    isAnalysisPhase,
    isCategorisationPhase,
    isResizePhase,
    showResizeProgress,
    showFaceProgress,
    showPaletteProgress,
    showAnalysisProgress,
    showCategorisationProgress,
    resizeCompletedCount,
    resizeTotalCount,
    faceCompletedCount,
    faceTotalCount,
    faceCountText,
    personsCount,
    personsCountText,
    faceProgressDetailText,
    paletteCompletedCount,
    paletteTotalCount,
    resizeCountText,
    paletteCountText,
    analysisCountText,
    categorisationCountText,
    resizeProgressDetailText,
    paletteProgressDetailText,
    analysisProgressDetailText,
    categorisationProgressDetailText,
    progressPercent,
    analysisCompletedCount,
    analysisTotalCount,
    analysisSummary,
    openaiConfigured,
    peopleAvailable,
    showStartFaceExtraction,
    showResumeFaceExtraction,
    showRerunFaceExtraction,
    showFaceExtractionActions,
    showAnalysisOpenAiHint,
    openSettingsTab,
    captionsAvailable,
    categoriesAvailable,
    showStartAnalysis,
    showResumeAnalysis,
    showRerunAnalysis,
    showAnalysisActions,
    showCategorisationOpenAiHint,
    showStartCategorisation,
    showResumeCategorisation,
    showRerunCategorisation,
    showCategorisationActions,
    categorisationCompletedCount,
    categorisationTotalCount,
    requestStatus,
    startProcessing,
    startPaletteExtraction,
    startFaceExtraction,
    rerunFaceExtraction,
    startAnalysis,
    rerunAnalysis,
    startCategorisation,
    rerunCategorisation,
  }
}
