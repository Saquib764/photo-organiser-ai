<script setup lang="ts">
import { categoryDisplayLabel, cycleTriState, folderDisplayName, whoInPhotoLabel } from '~/types/images'

const {
  folders,
  images,
  visibleCategories,
  filters,
  hasActiveFilters,
  loadingFolders,
  loadingImages,
  loadingCategories,
  error,
  imagesError,
  mediaUrl,
  fetchFolders,
  isFolderSelected,
  toggleFolder,
  setFilter,
  clearFilters,
  setPeopleRange,
  setQualityRange,
  toggleCategory,
  isCategorySelected,
  setUncategorizedOnly,
  categoriesAvailable,
  deleteImage,
  isDeleting,
} = useImageBrowser()

const { captionsAvailable } = useWorkspaceStatusDisplay()

const FILTERS_DISABLED_HINT = 'Add your OpenAI key in Settings to describe photos and use these filters.'
const CATEGORIES_DISABLED_HINT = 'Run categorisation in Library to group photos into story categories.'

const categorySearch = ref('')

const filteredCategories = computed(() => {
  const query = categorySearch.value.trim().toLowerCase()
  if (!query) {
    return visibleCategories.value
  }
  return visibleCategories.value.filter((category) => {
    const label = categoryDisplayLabel(category.id).toLowerCase()
    return label.includes(query) || category.description.toLowerCase().includes(query)
  })
})

function categoryFilterClass(active: boolean) {
  if (!categoriesAvailable.value) {
    return 'cursor-not-allowed border-gray-800 bg-gray-900/50 text-gray-600 opacity-50'
  }
  return active
    ? 'border-primary-500/50 bg-primary-500/15 text-primary-300'
    : 'border-gray-700 bg-gray-900 text-gray-500 hover:border-gray-600 hover:text-gray-400'
}

function toggleTriState(key: 'hasBride' | 'hasGroom' | 'hasOtherPeople') {
  if (!captionsAvailable.value) {
    return
  }
  setFilter(key, cycleTriState(filters.value[key]))
}

function disabledFilterClass(active: boolean) {
  if (!captionsAvailable.value) {
    return 'cursor-not-allowed border-gray-800 bg-gray-900/50 text-gray-600 opacity-50'
  }
  return active
    ? 'border-primary-500/50 bg-primary-500/15 text-primary-300'
    : 'border-gray-700 bg-gray-900 text-gray-500 hover:border-gray-600 hover:text-gray-400'
}

const whoInPhotoFilters = [
  { key: 'hasBride' as const, role: 'bride' },
  { key: 'hasGroom' as const, role: 'groom' },
  { key: 'hasOtherPeople' as const, role: 'guests' },
]

const peoplePresets = [
  { label: 'Any size', min: null, max: null },
  { label: '3 or more', min: 3, max: null },
  { label: '4 or more', min: 4, max: null },
  { label: '5 or more', min: 5, max: null },
] as const

const qualityPresets = [
  { label: 'Any', min: null, max: null },
  { label: 'Excellent (9+)', min: 9, max: null },
  { label: 'Great (7+)', min: 7, max: null },
  { label: 'Good (5+)', min: 5, max: null },
] as const

function isPeoplePresetActive(min: number | null, max: number | null) {
  return filters.value.minPeople === min && filters.value.maxPeople === max
}

function applyPeoplePreset(min: number | null, max: number | null) {
  setPeopleRange(min, max)
}

function isQualityPresetActive(min: number | null, max: number | null) {
  return filters.value.minQualityScore === min && filters.value.maxQualityScore === max
}

function applyQualityPreset(min: number | null, max: number | null) {
  setQualityRange(min, max)
}

const slideshowOpen = ref(false)

const canStartSlideshow = computed(
  () => folders.value.length > 0 && !loadingImages.value && images.value.length > 0,
)

function startSlideshow() {
  if (!canStartSlideshow.value) {
    return
  }
  slideshowOpen.value = true
}
</script>

<template>
  <div class="flex h-full min-h-0">
    <!-- Left: folders + filters -->
    <aside
      class="flex min-h-0 w-[var(--tf-folder-panel-width)] shrink-0 flex-col overflow-hidden border-r border-gray-800 bg-gray-900/50 p-5"
    >
      <div class="mb-4 shrink-0">
        <h2 class="tf-section-title mb-1">
          Image browser
        </h2>
        <p class="tf-section-subtitle">
          Browse processed thumbnails by folder
          <template v-if="captionsAvailable">
            and smart filters.
          </template>
        </p>
        <div
          v-if="folders.length > 0"
          class="mt-2 flex items-center gap-2"
        >
          <p class="text-xs text-gray-500">
            <template v-if="loadingImages">
              Loading images…
            </template>
            <template v-else>
              {{ images.length.toLocaleString() }}
              {{ images.length === 1 ? 'image' : 'images' }}
            </template>
          </p>
          <UButton
            v-if="canStartSlideshow"
            size="xs"
            color="primary"
            variant="soft"
            icon="i-heroicons-play"
            label="Slideshow"
            @click="startSlideshow"
          />
        </div>
      </div>

      <div class="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto">
      <div
        v-if="loadingFolders"
        class="flex items-center gap-2 text-sm text-gray-500"
      >
        <UIcon
          name="i-heroicons-arrow-path"
          class="size-4 animate-spin"
        />
        Loading folders…
      </div>

      <UAlert
        v-else-if="error"
        color="error"
        variant="subtle"
        icon="i-heroicons-exclamation-triangle"
        :title="error"
      >
        <template #description>
          <UButton
            class="mt-2"
            size="xs"
            color="neutral"
            variant="outline"
            label="Retry"
            @click="fetchFolders"
          />
        </template>
      </UAlert>

      <UAlert
        v-else-if="folders.length === 0"
        color="neutral"
        variant="subtle"
        icon="i-heroicons-folder"
        title="No folders yet"
        description="Add subfolders and images under workspace/raw/, then run processing."
      />

      <template v-else>
        <section class="space-y-2">
          <h3 class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
            Folders
          </h3>
          <div class="flex flex-col gap-1.5">
            <button
              v-for="folder in folders"
              :key="folder.name || '__root__'"
              type="button"
              class="inline-flex w-full cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-left text-xs font-medium transition-colors"
              :class="
                isFolderSelected(folder.name)
                  ? 'border-primary-500/50 bg-primary-500/15 text-primary-300'
                  : 'border-gray-700 bg-gray-900 text-gray-500 hover:border-gray-600 hover:text-gray-400'
              "
              @click="toggleFolder(folder.name)"
            >
              <UIcon
                :name="isFolderSelected(folder.name) ? 'i-heroicons-check-circle' : 'i-heroicons-folder'"
                class="size-4 shrink-0"
              />
              <span class="min-w-0 flex-1 truncate">
                {{ folderDisplayName(folder.name) }}
              </span>
              <span class="shrink-0 tabular-nums text-[10px] opacity-70">
                {{ folder.image_count }}
              </span>
            </button>
          </div>
        </section>

        <section
          class="space-y-3 border-t border-gray-800 pt-5"
          :class="{ 'opacity-90': !captionsAvailable }"
        >
          <div class="flex items-center justify-between gap-2">
            <h3 class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
              Find photos
            </h3>
            <UButton
              v-if="hasActiveFilters && (captionsAvailable || categoriesAvailable)"
              size="xs"
              color="neutral"
              variant="ghost"
              label="Clear"
              @click="clearFilters"
            />
          </div>

          <p
            v-if="!captionsAvailable"
            class="text-xs text-gray-500"
          >
            {{ FILTERS_DISABLED_HINT }}
          </p>

          <div
            class="flex flex-col gap-1.5"
            :class="{ 'pointer-events-none': !captionsAvailable }"
          >
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="item in whoInPhotoFilters"
                :key="item.key"
                type="button"
                :disabled="!captionsAvailable"
                class="inline-flex cursor-pointer items-center rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors"
                :class="disabledFilterClass(filters[item.key] !== null)"
                @click="toggleTriState(item.key)"
              >
                {{ whoInPhotoLabel(item.role, filters[item.key]) }}
              </button>
            </div>

            <div class="flex flex-wrap gap-1.5">
              <button
                type="button"
                :disabled="!captionsAvailable"
                class="inline-flex cursor-pointer items-center rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors"
                :class="disabledFilterClass(filters.isBlur === true)"
                @click="setFilter('isBlur', filters.isBlur === true ? null : true)"
              >
                Blurry
              </button>

              <button
                type="button"
                :disabled="!captionsAvailable"
                class="inline-flex cursor-pointer items-center rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors"
                :class="disabledFilterClass(filters.isBlur === false)"
                @click="setFilter('isBlur', filters.isBlur === false ? null : false)"
              >
                Sharp
              </button>
            </div>
          </div>

          <div
            class="space-y-2"
            :class="{ 'pointer-events-none': !captionsAvailable }"
          >
            <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
              Group size
            </span>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="preset in peoplePresets"
                :key="preset.label"
                type="button"
                :disabled="!captionsAvailable"
                class="inline-flex cursor-pointer rounded-full border px-2.5 py-1 text-xs font-medium transition-colors"
                :class="disabledFilterClass(isPeoplePresetActive(preset.min, preset.max))"
                @click="applyPeoplePreset(preset.min, preset.max)"
              >
                {{ preset.label }}
              </button>
            </div>
          </div>

          <div
            class="space-y-2"
            :class="{ 'pointer-events-none': !captionsAvailable }"
          >
            <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
              Photo quality
            </span>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="preset in qualityPresets"
                :key="preset.label"
                type="button"
                :disabled="!captionsAvailable"
                class="inline-flex cursor-pointer rounded-full border px-2.5 py-1 text-xs font-medium transition-colors"
                :class="disabledFilterClass(isQualityPresetActive(preset.min, preset.max))"
                @click="applyQualityPreset(preset.min, preset.max)"
              >
                {{ preset.label }}
              </button>
            </div>
          </div>

          <section
            class="space-y-2 border-t border-gray-800 pt-5"
            :class="{ 'opacity-90': !categoriesAvailable }"
          >
            <h3 class="text-[10px] font-bold uppercase tracking-widest text-gray-500">
              Story categories
            </h3>

            <p
              v-if="!categoriesAvailable"
              class="text-xs text-gray-500"
            >
              {{ CATEGORIES_DISABLED_HINT }}
            </p>

            <template v-else>
              <UInput
                v-model="categorySearch"
                size="xs"
                placeholder="Search categories…"
                icon="i-heroicons-magnifying-glass"
                :disabled="!categoriesAvailable"
                class="w-full"
              />

              <div
                class="flex max-h-48 flex-col gap-1 overflow-y-auto"
                :class="{ 'pointer-events-none': !categoriesAvailable }"
              >
                <p
                  v-if="loadingCategories"
                  class="text-xs text-gray-500"
                >
                  Loading categories…
                </p>
                <p
                  v-else-if="filteredCategories.length === 0"
                  class="text-xs text-gray-500"
                >
                  No categories in selected folders
                </p>
                <button
                  v-for="category in filteredCategories"
                  :key="category.id"
                  type="button"
                  :disabled="!categoriesAvailable"
                  class="inline-flex w-full cursor-pointer items-center gap-2 rounded-lg border px-2.5 py-1.5 text-left text-xs font-medium transition-colors"
                  :class="categoryFilterClass(isCategorySelected(category.id))"
                  :title="category.description"
                  @click="toggleCategory(category.id)"
                >
                  <span class="min-w-0 flex-1 truncate">
                    {{ categoryDisplayLabel(category.id) }}
                  </span>
                  <span class="shrink-0 tabular-nums text-[10px] opacity-70">
                    {{ category.image_count }}
                  </span>
                </button>
              </div>

              <button
                type="button"
                :disabled="!categoriesAvailable"
                class="inline-flex cursor-pointer items-center rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors"
                :class="categoryFilterClass(filters.uncategorizedOnly)"
                @click="setUncategorizedOnly(!filters.uncategorizedOnly)"
              >
                Uncategorized
              </button>
            </template>
          </section>
        </section>
      </template>
      </div>

      <div
        v-if="canStartSlideshow"
        class="mt-4 shrink-0 border-t border-gray-800 pt-4"
      >
        <UButton
          block
          size="lg"
          color="primary"
          icon="i-heroicons-play"
          label="Start slideshow"
          class="shadow-lg shadow-primary-500/25"
          @click="startSlideshow"
        />
      </div>
    </aside>

    <!-- Right: image grid (scrollable) -->
    <div class="relative flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-gray-950">
      <div class="min-h-0 flex-1 overflow-y-auto p-5">
        <UAlert
          v-if="imagesError"
          class="mb-4"
          color="error"
          variant="subtle"
          icon="i-heroicons-exclamation-triangle"
          :title="imagesError"
        />

        <div
          v-if="folders.length === 0"
          class="flex h-full min-h-[200px] flex-col items-center justify-center text-center"
        >
          <UIcon
            name="i-heroicons-photo"
            class="mb-2 size-10 text-gray-600"
          />
          <p class="text-sm text-gray-400">
            Add folders to browse images
          </p>
        </div>

        <div
          v-else-if="!loadingImages && images.length === 0"
          class="flex min-h-[200px] flex-col items-center justify-center rounded-lg border border-dashed border-gray-700 bg-gray-900/50 px-6 py-10 text-center"
        >
          <UIcon
            name="i-heroicons-photo"
            class="mb-2 size-8 text-gray-600"
          />
          <p class="text-sm text-gray-400">
            No images match your filters
          </p>
          <p class="mt-1 text-xs text-gray-600">
            <template v-if="hasActiveFilters">
              Adjust folders or filters on the left.
            </template>
            <template v-else>
              Select at least one folder on the left.
            </template>
          </p>
        </div>

        <div
          v-else
          class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6"
        >
          <figure
            v-for="image in images"
            :key="image.path"
            tabindex="0"
            class="group overflow-hidden rounded-lg border border-gray-800 bg-gray-900 outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50"
          >
            <div class="relative aspect-square overflow-hidden bg-gray-950">
              <img
                :src="mediaUrl(image.path)"
                :alt="image.caption || image.path"
                class="size-full object-cover transition-transform duration-200 group-hover:scale-105"
                loading="lazy"
              >
              <div
                class="absolute right-1.5 top-1.5 z-20 opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-within:opacity-100"
              >
                <UButton
                  size="xs"
                  color="error"
                  variant="solid"
                  icon="i-heroicons-trash"
                  :loading="isDeleting(image.path)"
                  :disabled="isDeleting(image.path)"
                  aria-label="Delete image"
                  class="shadow-md"
                  @click.stop="deleteImage(image.path)"
                />
              </div>
              <div
                class="absolute inset-x-0 bottom-0 z-10 select-text bg-black/75 px-2.5 py-2.5 opacity-0 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100"
              >
                <p
                  v-if="image.caption"
                  class="line-clamp-3 text-xs leading-snug text-white"
                  :title="image.caption"
                >
                  {{ image.caption }}
                </p>
                <p
                  v-else
                  class="truncate font-mono text-[10px] text-gray-400"
                  :title="image.path"
                >
                  {{ image.path }}
                </p>
                <div
                  v-if="
                    image.number_of_people > 0
                      || image.has_bride
                      || image.has_groom
                      || image.has_other_people
                      || (image.analyzed && image.is_blur)
                      || (image.analyzed && image.quality_score > 0)
                      || image.category_id
                  "
                  class="mt-1.5 flex flex-wrap gap-1"
                >
                  <span
                    v-if="image.number_of_people > 0"
                    class="rounded bg-white/15 px-1 py-px text-[9px] text-gray-200"
                  >
                    {{ image.number_of_people }} {{ image.number_of_people === 1 ? 'person' : 'people' }}
                  </span>
                  <span
                    v-if="image.has_bride"
                    class="rounded bg-primary-500/30 px-1 py-px text-[9px] text-primary-200"
                  >
                    Bride
                  </span>
                  <span
                    v-if="image.has_groom"
                    class="rounded bg-primary-500/30 px-1 py-px text-[9px] text-primary-200"
                  >
                    Groom
                  </span>
                  <span
                    v-if="image.has_other_people"
                    class="rounded bg-white/15 px-1 py-px text-[9px] text-gray-200"
                  >
                    Guests
                  </span>
                  <span
                    v-if="image.analyzed && image.is_blur"
                    class="rounded bg-amber-500/30 px-1 py-px text-[9px] text-amber-200"
                  >
                    Blurry
                  </span>
                  <span
                    v-if="image.analyzed && image.quality_score > 0"
                    class="rounded bg-white/15 px-1 py-px text-[9px] text-gray-200"
                  >
                    {{ image.quality_score.toFixed(1) }}/10
                  </span>
                  <span
                    v-if="image.category_id"
                    class="rounded bg-violet-500/30 px-1 py-px text-[9px] text-violet-200"
                    :title="image.category_id"
                  >
                    {{ categoryDisplayLabel(image.category_id) }}
                  </span>
                </div>
              </div>
            </div>
          </figure>
        </div>
      </div>
    </div>

    <ImageSlideshow
      v-model:open="slideshowOpen"
      :images="images"
    />
  </div>
</template>
