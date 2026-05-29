export const SLIDE_INTERVAL_MS = 4000
export const CONTROLS_IDLE_MS = 4000

export interface UseSlideshowViewerOptions {
  total: MaybeRefOrGetter<number>
  startIndex?: MaybeRefOrGetter<number>
  onIndexChange?: (index: number) => void
  onOpen?: (index: number) => void
  onClose?: () => void
}

export function useSlideshowViewer(
  open: Ref<boolean>,
  options: UseSlideshowViewerOptions,
) {
  const index = ref(0)
  const playing = ref(true)
  const controlsVisible = ref(true)
  const isFullscreen = ref(false)
  const rootRef = ref<HTMLElement | null>(null)

  let timer: ReturnType<typeof setInterval> | null = null
  let controlsIdleTimer: ReturnType<typeof setTimeout> | null = null

  const total = computed(() => toValue(options.total))
  const positionLabel = computed(() => `${index.value + 1} / ${total.value}`)

  const chromeClass = computed(() =>
    controlsVisible.value ? 'slideshow-chrome--visible' : 'slideshow-chrome--hidden',
  )

  function clearTimer() {
    if (timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }

  function clearControlsIdleTimer() {
    if (controlsIdleTimer !== null) {
      clearTimeout(controlsIdleTimer)
      controlsIdleTimer = null
    }
  }

  function scheduleControlsHide() {
    clearControlsIdleTimer()
    controlsIdleTimer = setTimeout(() => {
      controlsVisible.value = false
    }, CONTROLS_IDLE_MS)
  }

  function showControls() {
    controlsVisible.value = true
    scheduleControlsHide()
  }

  function onPointerActivity() {
    showControls()
  }

  function notifyIndexChange() {
    options.onIndexChange?.(index.value)
  }

  function startTimer() {
    clearTimer()
    if (!playing.value || !open.value || total.value <= 1) {
      return
    }
    timer = setInterval(() => {
      goNext()
    }, SLIDE_INTERVAL_MS)
  }

  function goNext() {
    if (total.value <= 1) {
      return
    }
    index.value = (index.value + 1) % total.value
    notifyIndexChange()
    if (playing.value) {
      startTimer()
    }
  }

  function goPrev() {
    if (total.value <= 1) {
      return
    }
    index.value = (index.value - 1 + total.value) % total.value
    notifyIndexChange()
    if (playing.value) {
      startTimer()
    }
  }

  function syncFullscreenState() {
    isFullscreen.value = document.fullscreenElement === rootRef.value
  }

  async function exitFullscreenIfActive() {
    if (document.fullscreenElement === rootRef.value) {
      try {
        await document.exitFullscreen()
      }
      catch {
        // Browser may reject if already exiting.
      }
    }
  }

  async function toggleFullscreen() {
    showControls()
    const el = rootRef.value
    if (!el) {
      return
    }

    try {
      if (document.fullscreenElement === el) {
        await document.exitFullscreen()
      }
      else {
        await el.requestFullscreen()
      }
    }
    catch {
      // Unsupported or blocked by browser policy.
    }
  }

  async function close() {
    await exitFullscreenIfActive()
    open.value = false
  }

  function togglePlay() {
    playing.value = !playing.value
    if (playing.value) {
      startTimer()
    }
    else {
      clearTimer()
    }
  }

  function onManualNav() {
    if (playing.value) {
      startTimer()
    }
  }

  function onOpen() {
    const start = toValue(options.startIndex) ?? 0
    index.value = Math.min(start, Math.max(0, total.value - 1))
    playing.value = true
    showControls()
    options.onOpen?.(index.value)
    notifyIndexChange()
    startTimer()
  }

  function onKeydown(event: KeyboardEvent) {
    if (!open.value) {
      return
    }
    showControls()
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
    }
    else if (event.key === 'ArrowRight') {
      event.preventDefault()
      goNext()
      onManualNav()
    }
    else if (event.key === 'ArrowLeft') {
      event.preventDefault()
      goPrev()
      onManualNav()
    }
    else if (event.key === ' ') {
      event.preventDefault()
      togglePlay()
    }
  }

  watch(open, (isOpen) => {
    if (isOpen) {
      onOpen()
    }
    else {
      void exitFullscreenIfActive()
      clearTimer()
      clearControlsIdleTimer()
      options.onClose?.()
    }
  })

  watch(total, () => {
    if (index.value >= total.value) {
      index.value = Math.max(0, total.value - 1)
    }
    if (open.value) {
      notifyIndexChange()
      startTimer()
    }
  })

  onMounted(() => {
    window.addEventListener('keydown', onKeydown)
    document.addEventListener('fullscreenchange', syncFullscreenState)
    if (open.value) {
      onOpen()
    }
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown)
    document.removeEventListener('fullscreenchange', syncFullscreenState)
    void exitFullscreenIfActive()
    clearTimer()
    clearControlsIdleTimer()
  })

  return {
    index,
    playing,
    controlsVisible,
    isFullscreen,
    rootRef,
    total,
    positionLabel,
    chromeClass,
    onPointerActivity,
    goNext,
    goPrev,
    togglePlay,
    toggleFullscreen,
    close,
    onManualNav,
    startTimer,
    showControls,
  }
}
