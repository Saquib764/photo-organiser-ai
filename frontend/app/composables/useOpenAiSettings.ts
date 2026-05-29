import type { OpenAiKeyStatus } from '~/types/settings'

export function useOpenAiSettings() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const status = ref<OpenAiKeyStatus | null>(null)
  const apiKeyInput = ref('')
  const loading = ref(false)
  const saving = ref(false)
  const removing = ref(false)
  const error = ref<string | null>(null)
  const saveSuccess = ref(false)

  async function fetchStatus() {
    loading.value = true
    error.value = null
    try {
      status.value = await $fetch<OpenAiKeyStatus>(`${apiBase}/api/v1/settings/openai-key`)
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load OpenAI settings'
      status.value = null
    }
    finally {
      loading.value = false
    }
  }

  async function saveKey() {
    const key = apiKeyInput.value.trim()
    if (!key) {
      error.value = 'Enter an API key to save'
      return
    }

    saving.value = true
    error.value = null
    saveSuccess.value = false
    try {
      status.value = await $fetch<OpenAiKeyStatus>(`${apiBase}/api/v1/settings/openai-key`, {
        method: 'PUT',
        body: { api_key: key },
      })
      apiKeyInput.value = ''
      saveSuccess.value = true
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to save API key'
    }
    finally {
      saving.value = false
    }
  }

  async function removeKey() {
    removing.value = true
    error.value = null
    saveSuccess.value = false
    try {
      await $fetch(`${apiBase}/api/v1/settings/openai-key`, { method: 'DELETE' })
      status.value = { configured: false, masked_key: null }
      apiKeyInput.value = ''
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to remove API key'
    }
    finally {
      removing.value = false
    }
  }

  onMounted(() => {
    void fetchStatus()
  })

  return {
    status,
    apiKeyInput,
    loading,
    saving,
    removing,
    error,
    saveSuccess,
    fetchStatus,
    saveKey,
    removeKey,
  }
}
