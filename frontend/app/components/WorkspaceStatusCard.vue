<script setup lang="ts">
const {
  status,
  analysisCompletedCount,
  analysisTotalCount,
  categorisationCompletedCount,
  categorisationTotalCount,
} = useWorkspaceStatusDisplay()

function formatCount(value: number | undefined) {
  return value === undefined ? '—' : value.toLocaleString()
}
</script>

<template>
  <section class="tf-card !p-0">
    <div class="border-b border-gray-800 px-5 py-4">
      <h3 class="tf-section-title">
        Library overview
      </h3>
      <p class="tf-section-subtitle !mt-1">
        Snapshot of your workspace—source files, prepared thumbnails, AI metadata, and story categories.
      </p>
    </div>

    <dl class="grid gap-px bg-gray-800 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <div class="bg-gray-900 px-5 py-4">
        <dt class="tf-card-label">
          Album folders
        </dt>
        <dd class="tf-card-value !mt-1">
          {{ formatCount(status?.total_folder_raw) }}
        </dd>
        <dd class="tf-card-hint">
          Top-level folders inside <code class="tf-code">raw/</code>
        </dd>
      </div>

      <div class="bg-gray-900 px-5 py-4">
        <dt class="tf-card-label">
          Original photos
        </dt>
        <dd class="tf-card-value !mt-1">
          {{ formatCount(status?.total_images_raw) }}
        </dd>
        <dd class="tf-card-hint">
          Full-size files in <code class="tf-code">raw/</code>
        </dd>
      </div>

      <div class="bg-gray-900 px-5 py-4">
        <dt class="tf-card-label">
          Thumbnails
        </dt>
        <dd class="tf-card-value !mt-1">
          {{ formatCount(status?.total_images_processed) }}
        </dd>
        <dd class="tf-card-hint">
          Resized copies in <code class="tf-code">processed_small/</code>
        </dd>
      </div>

      <div class="bg-gray-900 px-5 py-4">
        <dt class="tf-card-label">
          With captions
        </dt>
        <dd class="tf-card-value !mt-1">
          <template v-if="analysisTotalCount > 0">
            {{ formatCount(analysisCompletedCount) }}
            <span class="text-lg font-normal text-gray-500">
              / {{ formatCount(analysisTotalCount) }}
            </span>
          </template>
          <template v-else>
            —
          </template>
        </dd>
        <dd class="tf-card-hint">
          AI captions in <code class="tf-code">image_metadata.json</code>
        </dd>
      </div>

      <div class="bg-gray-900 px-5 py-4">
        <dt class="tf-card-label">
          Story categories
        </dt>
        <dd class="tf-card-value !mt-1">
          <template v-if="categorisationTotalCount > 0">
            {{ formatCount(status?.categories_count) }}
            <span class="text-lg font-normal text-gray-500">
              · {{ formatCount(categorisationCompletedCount) }}/{{ formatCount(categorisationTotalCount) }} photos
            </span>
          </template>
          <template v-else>
            {{ formatCount(status?.categories_count) }}
          </template>
        </dd>
        <dd class="tf-card-hint">
          Groups in <code class="tf-code">image_categories.json</code>
        </dd>
      </div>
    </dl>
  </section>
</template>
