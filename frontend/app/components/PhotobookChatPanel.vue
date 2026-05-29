<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
import { toUChatMessages } from '~/types/photobook'
import type { PhotobookDocument } from '~/types/photobook'

const props = defineProps<{
  document: PhotobookDocument | null
  chatLoading: boolean
  clearingSession: boolean
  disabled: boolean
  canStartSlideshow: boolean
}>()

const emit = defineEmits<{
  send: [message: string]
  clear: []
  slideshow: []
}>()

function isPristineSession(doc: PhotobookDocument | null): boolean {
  if (!doc) {
    return true
  }
  if (doc.chat.length > 0) {
    return false
  }
  if (doc.pages.some(p => (p.extra_images?.length ?? 0) > 0)) {
    return false
  }
  if (doc.pages.length !== 1) {
    return false
  }
  const page = doc.pages[0]
  if (!page) {
    return true
  }
  return (
    page.status === 'draft'
    && !page.narrative.trim()
    && !page.layout_id
    && Object.keys(page.slots).length === 0
    && Object.keys(page.text_slots ?? {}).length === 0
    && page.title === 'Page 1'
  )
}

const canClearSession = computed(() => !isPristineSession(props.document))

const showClearConfirm = ref(false)

const draft = ref('')

const {
  templates: promptTemplates,
  loadingList: promptTemplatesLoading,
  loadingContent: promptTemplateContentLoading,
  listError: promptTemplatesError,
  loadTemplates,
  fetchTemplateContent,
} = usePromptTemplates()

onMounted(() => {
  void loadTemplates()
})

const templateMenuItems = computed<DropdownMenuItem[][]>(() => {
  if (!promptTemplates.value.length) {
    return [[{
      label: promptTemplatesLoading.value
        ? 'Loading ideas…'
        : (promptTemplatesError.value ?? 'No template ideas found'),
      disabled: true,
    }]]
  }
  return [
    promptTemplates.value.map(template => ({
      label: template.name,
      onSelect: () => {
        void applyTemplate(template.id)
      },
    })),
  ]
})

async function applyTemplate(templateId: string) {
  if (props.disabled || props.chatLoading || promptTemplateContentLoading.value) {
    return
  }
  try {
    draft.value = await fetchTemplateContent(templateId)
  } catch {
    // Keep existing draft on failure.
  }
}

const chatMessages = computed(() =>
  toUChatMessages(props.document?.chat ?? []),
)

const chatStatus = computed(() => (props.chatLoading ? 'submitted' : 'ready'))

const clearDisabled = computed(
  () =>
    !canClearSession.value
    || props.disabled
    || props.chatLoading
    || props.clearingSession,
)

const slideshowDisabled = computed(
  () => !props.canStartSlideshow || props.disabled,
)

function onSubmit() {
  const text = draft.value.trim()
  if (!text || props.disabled || props.chatLoading) {
    return
  }
  emit('send', text)
  draft.value = ''
}

function onClearClick() {
  if (clearDisabled.value) {
    return
  }
  showClearConfirm.value = true
}

function onConfirmClear() {
  showClearConfirm.value = false
  emit('clear')
}
</script>

<template>
  <div class="flex h-full min-h-0 flex-col border-r border-gray-800 bg-gray-900/50">
    <div class="shrink-0 border-b border-gray-800 p-4">
      <div class="flex items-center gap-2">
        <UButton
          size="xs"
          variant="soft"
          color="primary"
          icon="i-heroicons-play"
          label="Slideshow"
          :disabled="slideshowDisabled"
          @click="emit('slideshow')"
        />
        <UButton
          size="xs"
          variant="ghost"
          color="neutral"
          icon="i-heroicons-trash"
          label="Clear session"
          :disabled="clearDisabled"
          :loading="clearingSession"
          @click="onClearClick"
        />
      </div>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto p-3">
      <UChatMessages
        v-if="chatMessages.length"
        :messages="chatMessages"
        :status="chatStatus"
        class="gap-3"
        :ui="{ root: 'gap-3' }"
      />
      <p
        v-else
        class="px-2 py-6 text-center text-xs text-gray-600"
      >
        Example: “Create a 8-page photobook for our wedding, starting with welcome shots, then ceremony and reception.”
      </p>
    </div>

    <div class="shrink-0 border-t border-gray-800 p-3">
      <UChatPrompt
        v-model="draft"
        placeholder="Describe your photobook…"
        :maxrows="7"
        :disabled="disabled || chatLoading"
        :loading="chatLoading"
        :ui="{ base: 'overflow-y-auto' }"
        @submit="onSubmit"
      >
        <template #footer>
          <div class="flex items-center gap-2 px-1 pb-1">
            <UDropdownMenu
              :items="templateMenuItems"
              :disabled="disabled || chatLoading || promptTemplateContentLoading"
            >
              <UButton
                size="xs"
                variant="soft"
                color="neutral"
                icon="i-heroicons-light-bulb"
                label="Template idea"
                :loading="promptTemplatesLoading || promptTemplateContentLoading"
                :disabled="disabled || chatLoading"
              />
            </UDropdownMenu>
          </div>
        </template>
      </UChatPrompt>
    </div>

    <UModal
      v-model:open="showClearConfirm"
      title="Clear entire session?"
      :dismissible="!clearingSession"
    >
      <template #body>
        <p class="text-sm text-gray-300">
          This will permanently delete your whole photobook session, including:
        </p>
        <ul class="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-400">
          <li>All chat messages</li>
          <li>Your storyboard (page plans and narratives)</li>
          <li>Your composed photobook (layouts, slots, and extras)</li>
        </ul>
        <p class="mt-4 text-sm text-gray-300">
          Your uploaded images in the library will <span class="font-medium text-gray-200">not</span> be deleted.
        </p>
      </template>

      <template #footer="{ close }">
        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="ghost"
            :disabled="clearingSession"
            @click="close"
          />
          <UButton
            label="Clear session"
            color="error"
            :loading="clearingSession"
            @click="onConfirmClear"
          />
        </div>
      </template>
    </UModal>
  </div>
</template>
