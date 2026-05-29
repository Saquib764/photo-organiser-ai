<script setup lang="ts">
const {
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
} = useOpenAiSettings()
</script>

<template>
  <div class="flex h-full min-h-0">
    <!-- Left: title (fixed, no scroll) -->
    <aside
      class="flex w-[var(--tf-folder-panel-width)] shrink-0 flex-col overflow-hidden border-r border-gray-800 bg-gray-900/50 p-6 lg:p-8"
    >
      <div class="mb-4 flex size-12 items-center justify-center rounded-xl border border-gray-800 bg-gray-900 shadow-lg shadow-black/20">
        <UIcon
          name="i-heroicons-cog-6-tooth"
          class="size-6 text-primary-400"
        />
      </div>
      <h2 class="tf-page-title">
        Settings
      </h2>
      <p class="mt-3 text-sm leading-relaxed text-gray-500">
        Configure workspace integrations and preferences. Changes apply to your local photo library immediately.
      </p>
    </aside>

    <!-- Right: integrations (scrollable) -->
    <div class="min-h-0 min-w-0 flex-1 overflow-y-auto p-6 lg:p-8">
      <section
        class="mx-auto max-w-2xl overflow-hidden rounded-xl border border-gray-800 bg-gray-900 shadow-xl shadow-black/25"
      >
        <div class="border-b border-gray-800 bg-gradient-to-r from-primary-500/10 via-gray-900 to-gray-900 px-6 py-5 sm:px-8">
          <div class="flex items-start gap-4">
            <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary-500/20 bg-primary-500/10">
              <UIcon
                name="i-heroicons-sparkles"
                class="size-5 text-primary-400"
              />
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="text-base font-semibold text-white">
                OpenAI
              </h3>
              <p class="mt-1 text-sm leading-relaxed text-gray-400">
                Powers AI captions and wedding metadata for your photos. The key is saved in your workspace, not in
                <code class="tf-code">.env</code>.
              </p>
            </div>
          </div>
        </div>

        <div class="space-y-6 px-6 py-7 sm:px-8 sm:py-8">
          <div
            v-if="loading"
            class="flex items-center justify-center gap-2 rounded-lg border border-dashed border-gray-800 bg-gray-950/80 py-12 text-sm text-gray-500"
          >
            <UIcon
              name="i-heroicons-arrow-path"
              class="size-4 animate-spin"
            />
            Loading settings…
          </div>

          <template v-else>
            <div class="flex flex-wrap items-center gap-3">
              <span
                class="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium"
                :class="
                  status?.configured
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
                    : 'border-gray-700 bg-gray-950 text-gray-500'
                "
              >
                <span
                  class="size-1.5 rounded-full"
                  :class="status?.configured ? 'bg-emerald-400' : 'bg-gray-600'"
                />
                {{ status?.configured ? 'Connected' : 'Not configured' }}
              </span>
              <span
                v-if="status?.configured && status.masked_key"
                class="font-mono text-xs text-gray-500"
              >
                {{ status.masked_key }}
              </span>
            </div>

            <div
              v-if="error || saveSuccess"
              class="space-y-3"
            >
              <UAlert
                v-if="error"
                color="error"
                variant="subtle"
                icon="i-heroicons-exclamation-triangle"
                :title="error"
              />
              <UAlert
                v-if="saveSuccess"
                color="success"
                variant="subtle"
                icon="i-heroicons-check"
                title="API key saved successfully"
              />
            </div>

            <form
              class="space-y-6"
              @submit.prevent="saveKey"
            >
              <div class="rounded-lg border border-gray-800 bg-gray-950/80 p-5 sm:p-6">
                <UFormField
                  label="API key"
                  hint="Paste a new key to replace the one on disk."
                  class="[&_label]:text-xs [&_label]:font-bold [&_label]:uppercase [&_label]:tracking-widest [&_label]:text-gray-500"
                >
                  <UInput
                    v-model="apiKeyInput"
                    type="password"
                    name="openai_api_key"
                    placeholder="sk-…"
                    autocomplete="off"
                    size="lg"
                    class="w-full"
                    :ui="{
                      base: 'bg-gray-900 ring-gray-700 focus:ring-primary-500/50',
                    }"
                  />
                </UFormField>
              </div>

              <div class="flex flex-col gap-3 border-t border-gray-800 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <p class="text-xs text-gray-600">
                  Keys are stored in
                  <code class="tf-code">workspace/openai_config.json</code>
                </p>
                <div class="flex flex-wrap gap-2">
                  <UButton
                    type="submit"
                    color="primary"
                    icon="i-heroicons-check"
                    label="Save key"
                    size="md"
                    :loading="saving"
                    :disabled="!apiKeyInput.trim()"
                    class="shadow-lg shadow-primary-500/20"
                  />
                  <UButton
                    v-if="status?.configured"
                    type="button"
                    color="neutral"
                    variant="outline"
                    icon="i-heroicons-trash"
                    label="Remove"
                    size="md"
                    :loading="removing"
                    @click="removeKey"
                  />
                  <UButton
                    type="button"
                    color="neutral"
                    variant="ghost"
                    icon="i-heroicons-arrow-path"
                    label="Refresh"
                    size="md"
                    @click="fetchStatus"
                  />
                </div>
              </div>
            </form>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>
