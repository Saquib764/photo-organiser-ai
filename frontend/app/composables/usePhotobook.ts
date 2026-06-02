import { useDebounceFn, useNow } from '@vueuse/core'
import type {
  PhotobookChatResponse,
  PhotobookDocument,
  PhotobookPage,
  PhotobookResponse,
  SlotOffset,
} from '~/types/photobook'
import { anyPageCanCompose, canComposePage } from '~/utils/photobookCompose'

function fetchErrorMessage(e: unknown, fallback: string): string {
  const err = e as { data?: { detail?: string }, message?: string }
  return err.data?.detail ?? err.message ?? fallback
}

export function usePhotobook() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const document = ref<PhotobookDocument | null>(null)
  const loading = ref(false)
  const chatLoading = ref(false)
  const error = ref<string | null>(null)

  const pages = computed(() => document.value?.pages ?? [])
  const activePageId = ref<string | null>(null)

  const activePage = computed<PhotobookPage | null>(() => {
    if (!activePageId.value || !document.value) {
      return null
    }
    return document.value.pages.find(p => p.id === activePageId.value) ?? null
  })

  const extraImages = computed(() => activePage.value?.extra_images ?? [])

  const now = useNow({ interval: 1000 })

  const activePageCanCompose = computed(() => {
    const page = activePage.value
    if (!page) {
      return false
    }
    return canComposePage(page, now.value.getTime())
  })

  const canComposeAll = computed(() =>
    anyPageCanCompose(pages.value, now.value.getTime()),
  )

  watch(pages, (list) => {
    if (!list.length) {
      activePageId.value = null
      return
    }
    if (!activePageId.value || !list.some(p => p.id === activePageId.value)) {
      activePageId.value = list[0].id
    }
  }, { immediate: true })

  function applyResponse(data: PhotobookResponse) {
    document.value = data.document
  }

  function pageById(pageId: string) {
    return document.value?.pages.find(p => p.id === pageId)
  }

  async function patchPage(
    pageId: string,
    body: Record<string, unknown>,
    errorLabel: string,
  ) {
    error.value = null
    try {
      const data = await $fetch<PhotobookResponse>(
        `${apiBase}/api/v1/photobook/pages/${encodeURIComponent(pageId)}`,
        { method: 'PATCH', body },
      )
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, errorLabel)
      await fetchPhotobook()
    }
  }

  const debouncedPatchPage = useDebounceFn(
    (pageId: string, body: Record<string, unknown>, errorLabel: string) =>
      patchPage(pageId, body, errorLabel),
    250,
  )

  async function fetchPhotobook() {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<PhotobookResponse>(`${apiBase}/api/v1/photobook`)
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Failed to load photobook')
    }
    finally {
      loading.value = false
    }
  }

  const clearingSession = ref(false)

  async function clearSession() {
    error.value = null
    clearingSession.value = true
    try {
      const data = await $fetch<PhotobookResponse>(`${apiBase}/api/v1/photobook/chat`, {
        method: 'DELETE',
      })
      applyResponse(data)
      activePageId.value = data.document.pages[0]?.id ?? null
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Failed to clear session')
      await fetchPhotobook()
    }
    finally {
      clearingSession.value = false
    }
  }

  async function sendChatMessage(message: string) {
    const text = message.trim()
    if (!text) {
      return
    }

    chatLoading.value = true
    error.value = null

    // Optimistic local echo (will be replaced by server response).
    if (document.value) {
      document.value.chat.push({
        id: `msg-local-user-${Date.now()}`,
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      })
    }

    try {
      const data = await $fetch<PhotobookChatResponse>(`${apiBase}/api/v1/photobook/chat`, {
        method: 'POST',
        body: { message: text },
      })
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Chat failed')
      await fetchPhotobook()
    }
    finally {
      chatLoading.value = false
    }
  }

  async function addPage(title = 'New page', narrative = '') {
    error.value = null
    try {
      const data = await $fetch<PhotobookResponse>(`${apiBase}/api/v1/photobook/pages`, {
        method: 'POST',
        body: { title, narrative },
      })
      applyResponse(data)
      const last = data.document.pages.at(-1)
      if (last) {
        activePageId.value = last.id
      }
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Failed to add page')
    }
  }

  function applyPageOrder(pageIds: string[]) {
    if (!document.value) {
      return
    }
    const byId = Object.fromEntries(document.value.pages.map(page => [page.id, page]))
    document.value.pages = pageIds
      .map(id => byId[id])
      .filter((page): page is PhotobookPage => Boolean(page))
  }

  async function reorderPages(pageIds: string[]) {
    if (!document.value || pageIds.length < 2) {
      return
    }

    const currentIds = document.value.pages.map(page => page.id)
    if (
      pageIds.length !== currentIds.length
      || pageIds.every((id, index) => id === currentIds[index])
    ) {
      return
    }

    applyPageOrder(pageIds)
    error.value = null
    try {
      const data = await $fetch<PhotobookResponse>(
        `${apiBase}/api/v1/photobook/pages/order`,
        { method: 'PUT', body: { page_ids: pageIds } },
      )
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Failed to reorder pages')
      await fetchPhotobook()
    }
  }

  function shufflePages() {
    const ids = pages.value.map(page => page.id)
    if (ids.length < 2) {
      return
    }
    const shuffled = [...ids]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      const tmp = shuffled[i]!
      shuffled[i] = shuffled[j]!
      shuffled[j] = tmp
    }
    if (shuffled.every((id, index) => id === ids[index])) {
      shuffled.push(shuffled.shift()!)
    }
    void reorderPages(shuffled)
  }

  async function removePage(pageId: string) {
    if (pages.value.length <= 1) {
      return
    }

    error.value = null
    try {
      const data = await $fetch<PhotobookResponse>(
        `${apiBase}/api/v1/photobook/pages/${encodeURIComponent(pageId)}`,
        { method: 'DELETE' },
      )
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Failed to delete page')
      await fetchPhotobook()
    }
  }

  async function composePage(pageId: string) {
    error.value = null

    const page = pageById(pageId)
    if (page && !canComposePage(page, now.value.getTime())) {
      return
    }

    if (page) {
      page.status = 'composing'
      page.composing_started_at = new Date().toISOString()
      page.error_message = null
    }

    try {
      const data = await $fetch<PhotobookResponse>(
        `${apiBase}/api/v1/photobook/pages/${encodeURIComponent(pageId)}/compose`,
        { method: 'POST' },
      )
      applyResponse(data)
    }
    catch (e) {
      error.value = fetchErrorMessage(e, 'Compose failed')
      await fetchPhotobook()
    }
  }

  async function composeAll() {
    const at = now.value.getTime()
    for (const page of pages.value) {
      if (page.narrative.trim() && canComposePage(page, at)) {
        await composePage(page.id)
      }
    }
  }

  function setImageBorderRadius(pageId: string, radius: number) {
    const page = pageById(pageId)
    if (page) {
      page.image_border_radius = radius
    }
    void debouncedPatchPage(
      pageId,
      { image_border_radius: radius },
      'Failed to update corner radius',
    )
  }

  function setBackgroundColor(pageId: string, color: string) {
    const page = pageById(pageId)
    if (page) {
      page.background_color = color
    }
    void patchPage(pageId, { background_color: color }, 'Failed to update sheet color')
  }

  function setTextSlot(pageId: string, slotId: string, text: string) {
    const page = pageById(pageId)
    if (!page?.layout_id) {
      return
    }

    const nextTextSlots = {
      ...(page.text_slots ?? {}),
      [slotId]: { ...(page.text_slots?.[slotId] ?? {}), text },
    }
    page.text_slots = nextTextSlots

    void debouncedPatchPage(
      pageId,
      { text_slots: { [slotId]: { text } } },
      'Failed to update text',
    )
  }

  function setSlotOffset(pageId: string, slotId: string, offset: SlotOffset) {
    const page = pageById(pageId)
    if (!page) {
      return
    }
    const slotOffsets = { ...(page.slot_offsets ?? {}), [slotId]: offset }
    page.slot_offsets = slotOffsets
    void debouncedPatchPage(
      pageId,
      { slot_offsets: slotOffsets },
      'Failed to update image position',
    )
  }

  async function assignSlot(pageId: string, slotId: string, imagePath: string) {
    const page = pageById(pageId)
    if (!page?.layout_id) {
      return
    }

    const previousPath = page.slots?.[slotId]
    const nextSlots = { ...page.slots, [slotId]: imagePath }

    const nextSlotOffsets = { ...(page.slot_offsets ?? {}) }
    if (previousPath !== imagePath) {
      delete nextSlotOffsets[slotId]
    }

    // Swap: remove clicked image from extras; if the slot had an image, put it back into extras.
    const nextExtras = (() => {
      const base = extraImages.value.filter(p => p !== imagePath)
      if (!previousPath || previousPath === imagePath) {
        return base
      }
      if (base.includes(previousPath)) {
        return base
      }
      return [previousPath, ...base]
    })()

    // Optimistic update so rapid slot swaps do not read stale extra_images.
    page.slots = nextSlots
    page.slot_offsets = nextSlotOffsets
    page.extra_images = nextExtras

    await patchPage(
      pageId,
      {
        slots: nextSlots,
        slot_offsets: nextSlotOffsets,
        layout_id: page.layout_id,
        extra_images: nextExtras,
      },
      'Failed to update page',
    )
  }

  onMounted(() => {
    void fetchPhotobook()
  })

  return {
    document,
    pages,
    extraImages,
    activePageId,
    activePage,
    activePageCanCompose,
    canComposeAll,
    loading,
    chatLoading,
    error,
    fetchPhotobook,
    clearingSession,
    clearSession,
    sendChatMessage,
    addPage,
    reorderPages,
    shufflePages,
    removePage,
    composePage,
    composeAll,
    assignSlot,
    setImageBorderRadius,
    setBackgroundColor,
    setSlotOffset,
    setTextSlot,
  }
}
