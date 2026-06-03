<script setup lang="ts">
const {
  flags,
  processingBusy,
  connectionState,
  openaiConfigured,
  openSettingsTab,
} = useWorkspaceStatusDisplay()
</script>

<template>
  <div class="space-y-8">
    <section>
      <h2 class="tf-section-title mb-1">
        Processing pipeline
      </h2>
      <p class="tf-section-subtitle mb-4">
        Prepare your library in order: thumbnails, people, colours, captions, then story categories.
        Start each step from its card when the previous one is complete.
      </p>
      <LibraryFlagsPanel />
    </section>

    <WorkspaceStatusCard />

    <section>
      <h2 class="tf-section-title mb-1">
        Next steps
      </h2>
      <p class="tf-section-subtitle mb-4">
        Guidance based on where your library is in the pipeline.
      </p>

      <UAlert
        v-if="!flags.image_found"
        color="primary"
        variant="subtle"
        icon="i-heroicons-arrow-up-tray"
        title="Add photos to begin"
        class="border-primary-500/20 bg-primary-500/10"
      >
        <template #description>
          <p class="text-sm text-gray-400">
            Copy your image files into
            <code class="tf-code">workspace/raw/</code>.
            You can use subfolders for albums, days, or events.
          </p>
        </template>
      </UAlert>

      <UAlert
        v-else-if="flags.categorisation_complete"
        color="success"
        variant="subtle"
        icon="i-heroicons-check-circle"
        title="Your library is ready"
        description="Thumbnails, colours, captions, and categories are complete. Open Photobook chat to plan pages."
      />

      <UAlert
        v-else-if="flags.image_analysis_complete && !processingBusy && openaiConfigured"
        color="primary"
        variant="subtle"
        icon="i-heroicons-squares-2x2"
        title="Ready to categorise"
        class="border-primary-500/20 bg-primary-500/10"
        description="Captions are done. Press Start on the Categorise card to group photos into story categories for planning."
      />

      <UAlert
        v-else-if="flags.image_analysis_complete && !processingBusy && !openaiConfigured"
        color="warning"
        variant="subtle"
        icon="i-heroicons-key"
        title="OpenAI API key needed"
        class="border-amber-500/20 bg-amber-500/10"
      >
        <template #description>
          <p class="text-sm text-gray-400">
            Categorising photos uses OpenAI. Add your API key in
            <button
              type="button"
              class="text-primary-400 underline decoration-primary-400/40 underline-offset-2 hover:text-primary-300"
              @click="openSettingsTab"
            >
              Settings
            </button>
            to continue.
          </p>
        </template>
      </UAlert>

      <UAlert
        v-else-if="flags.resize_complete && !flags.has_analysed_color && !processingBusy"
        color="primary"
        variant="subtle"
        icon="i-heroicons-swatch"
        title="Thumbnails are ready"
        class="border-primary-500/20 bg-primary-500/10"
        description="Resize is complete. Run Colours next, then Captions when you are ready for AI metadata."
      />

      <UAlert
        v-else-if="
          flags.has_analysed_color
            && !flags.image_analysis_complete
            && !processingBusy
            && !openaiConfigured
        "
        color="warning"
        variant="subtle"
        icon="i-heroicons-key"
        title="OpenAI API key needed"
        class="border-amber-500/20 bg-amber-500/10"
      >
        <template #description>
          <p class="text-sm text-gray-400">
            Caption analysis uses OpenAI. Add your API key in
            <button
              type="button"
              class="text-primary-400 underline decoration-primary-400/40 underline-offset-2 hover:text-primary-300"
              @click="openSettingsTab"
            >
              Settings
            </button>
            to continue.
          </p>
        </template>
      </UAlert>

      <UAlert
        v-else-if="flags.has_analysed_color && !flags.image_analysis_complete && !processingBusy && openaiConfigured"
        color="primary"
        variant="subtle"
        icon="i-heroicons-check-circle"
        title="Colours are ready"
        class="border-primary-500/20 bg-primary-500/10"
        description="Dominant colours are saved. Press Start on the Captions card when you want AI descriptions for every photo."
      />

      <UAlert
        v-else-if="connectionState !== 'open'"
        color="neutral"
        variant="subtle"
        icon="i-heroicons-signal"
        title="Not connected to server"
        description="Start the backend and wait for the connection indicator to turn green."
      />
    </section>
  </div>
</template>
