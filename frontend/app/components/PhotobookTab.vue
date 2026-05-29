<script setup lang="ts">
import { getPageLayout } from '~/constants/pageLayouts'

const {
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
  clearingSession,
  clearSession,
  sendChatMessage,
  addPage,
  removePage,
  composePage,
  composeAll,
  assignSlot,
  setImageBorderRadius,
  setBackgroundColor,
  setSlotOffset,
  setTextSlot,
} = usePhotobook()

const { status: openAiStatus } = useOpenAiSettings()

const openAiConfigured = computed(() => openAiStatus.value?.configured ?? false)

const focusedSlotId = ref<string | null>(null)
const { aspectRatio } = usePhotobookUiPrefs()

const layoutSlotIds = computed(() => {
  const layoutId = activePage.value?.layout_id
  if (!layoutId) {
    return []
  }
  return getPageLayout(layoutId)?.slots.map(s => s.id) ?? []
})

watch(activePage, () => {
  focusedSlotId.value = layoutSlotIds.value[0] ?? null
})

function onAssignExtra(path: string) {
  if (activePageId.value && focusedSlotId.value) {
    void assignSlot(activePageId.value, focusedSlotId.value, path)
  }
}

const slideshowOpen = ref(false)

const canStartSlideshow = computed(() => !loading.value && pages.value.length > 0)

const slideshowStartIndex = computed(() => {
  const idx = pages.value.findIndex(p => p.id === activePageId.value)
  return Math.max(0, idx)
})

function startSlideshow() {
  if (!canStartSlideshow.value) {
    return
  }
  slideshowOpen.value = true
}

</script>

<template>
  <div class="flex h-full min-h-0">
    <aside class="w-[var(--tf-folder-panel-width)] shrink-0">
      <PhotobookChatPanel
        :document="document"
        :chat-loading="chatLoading"
        :clearing-session="clearingSession"
        :disabled="!openAiConfigured"
        :can-start-slideshow="canStartSlideshow"
        @send="sendChatMessage"
        @clear="clearSession"
        @slideshow="startSlideshow"
      />
    </aside>

    <div class="flex min-h-0 min-w-0 flex-1 flex-col">
      <div
        v-if="!openAiConfigured"
        class="shrink-0 border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-200"
      >
        Add your OpenAI API key in
        <span class="font-semibold">Settings</span>
        to use photobook chat and compose.
      </div>

      <UAlert
        v-if="error"
        color="error"
        variant="soft"
        :title="error"
        class="mx-4 mt-3 shrink-0"
      />

      <div
        v-if="loading"
        class="flex flex-1 items-center justify-center gap-2 text-sm text-gray-500"
      >
        <UIcon
          name="i-heroicons-arrow-path"
          class="size-5 animate-spin"
        />
        Loading photobook…
      </div>

      <template v-else>
        <PhotobookPageTabs
          v-model:active-page-id="activePageId"
          :pages="pages"
          :open-ai-configured="openAiConfigured"
          :can-compose-active-page="activePageCanCompose"
          :can-compose-all="canComposeAll"
          @add-page="addPage()"
          @delete-page="removePage"
          @compose-page="activePage && composePage(activePage.id)"
          @compose-all="composeAll()"
        />

        <div class="min-h-0 flex-1 overflow-hidden p-0">
          <PhotobookPagePreview
            :page="activePage"
            :aspect-ratio="aspectRatio"
            @set-image-border-radius="(radius) => activePageId && setImageBorderRadius(activePageId, radius)"
            @set-background-color="(color) => activePageId && setBackgroundColor(activePageId, color)"
            @slot-offset-change="(slotId, offset) => activePageId && setSlotOffset(activePageId, slotId, offset)"
            @text-slot-change="(slotId, text) => activePageId && setTextSlot(activePageId, slotId, text)"
          />
        </div>
      </template>
    </div>

    <aside class="w-[var(--tf-photobook-extra-width)] shrink-0">
      <PhotobookExtraImages
        :paths="extraImages"
        v-model:focused-slot-id="focusedSlotId"
        :layout-slot-ids="layoutSlotIds"
        @assign="onAssignExtra"
      />
    </aside>

    <PhotobookPageSlideshow
      v-model:open="slideshowOpen"
      :pages="pages"
      :aspect-ratio="aspectRatio"
      :start-index="slideshowStartIndex"
    />
  </div>
</template>
