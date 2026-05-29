import type {
  PromptTemplateContentResponse,
  PromptTemplateListResponse,
  PromptTemplateSummary,
} from '~/types/promptTemplates'

export function usePromptTemplates() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const templates = ref<PromptTemplateSummary[]>([])
  const loadingList = ref(false)
  const loadingContent = ref(false)
  const listError = ref<string | null>(null)

  async function loadTemplates() {
    loadingList.value = true
    listError.value = null
    try {
      const data = await $fetch<PromptTemplateListResponse>(
        `${apiBase}/api/v1/prompt-templates`,
      )
      templates.value = data.templates
    } catch (err) {
      listError.value = err instanceof Error ? err.message : 'Failed to load templates'
      templates.value = []
    } finally {
      loadingList.value = false
    }
  }

  async function fetchTemplateContent(templateId: string): Promise<string> {
    loadingContent.value = true
    try {
      const data = await $fetch<PromptTemplateContentResponse>(
        `${apiBase}/api/v1/prompt-templates/${encodeURIComponent(templateId)}`,
      )
      return data.content
    } finally {
      loadingContent.value = false
    }
  }

  return {
    templates,
    loadingList,
    loadingContent,
    listError,
    loadTemplates,
    fetchTemplateContent,
  }
}
