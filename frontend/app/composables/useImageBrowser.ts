import type { FolderInfo, ImageCategoryInfo, ImageEntry, ImageFilters } from '~/types/images'
import { EMPTY_IMAGE_FILTERS, folderApiToken } from '~/types/images'

function appendFilterParams(params: URLSearchParams, filters: ImageFilters) {
  if (filters.hasBride !== null) {
    params.set('has_bride', String(filters.hasBride))
  }
  if (filters.hasGroom !== null) {
    params.set('has_groom', String(filters.hasGroom))
  }
  if (filters.hasOtherPeople !== null) {
    params.set('has_other_people', String(filters.hasOtherPeople))
  }
  if (filters.minPeople !== null) {
    params.set('min_people', String(filters.minPeople))
  }
  if (filters.maxPeople !== null) {
    params.set('max_people', String(filters.maxPeople))
  }
  if (filters.analyzed !== null) {
    params.set('analyzed', String(filters.analyzed))
  }
  if (filters.isBlur !== null) {
    params.set('is_blur', String(filters.isBlur))
  }
  if (filters.minQualityScore !== null) {
    params.set('min_quality_score', String(filters.minQualityScore))
  }
  if (filters.maxQualityScore !== null) {
    params.set('max_quality_score', String(filters.maxQualityScore))
  }
  for (const id of filters.categoryIds) {
    params.append('categories', id)
  }
  if (filters.uncategorizedOnly) {
    params.set('uncategorized', 'true')
  }
}

function appendFolderParams(params: URLSearchParams, folderNames: Set<string>) {
  for (const name of folderNames) {
    params.append('folders', folderApiToken(name))
  }
}

export function useImageBrowser() {
  const { apiBase, mediaUrl, rawUrl } = useImageUrls()
  const { captionsAvailable, status } = useWorkspaceStatusDisplay()

  const folders = ref<FolderInfo[]>([])
  const selectedFolders = ref<Set<string>>(new Set())
  const categories = ref<ImageCategoryInfo[]>([])

  /** True when image_categories.json has at least one category (from API, not WebSocket). */
  const categoriesAvailable = computed(() => categories.value.length > 0)
  const images = ref<ImageEntry[]>([])
  const filters = ref<ImageFilters>({ ...EMPTY_IMAGE_FILTERS })
  const loadingFolders = ref(false)
  const loadingImages = ref(false)
  const loadingCategories = ref(false)
  const deletingPaths = ref<Set<string>>(new Set())
  /** Folder list fetch failures (sidebar). */
  const error = ref<string | null>(null)
  /** Image list fetch failures (grid); does not clear folders. */
  const imagesError = ref<string | null>(null)

  function imageDeleteUrl(path: string): string {
    const encoded = path.split('/').map(segment => encodeURIComponent(segment)).join('/')
    return `${apiBase}/api/v1/images/${encoded}`
  }

  const hasActiveFilters = computed(() =>
    Object.entries(filters.value).some(([key, value]) => {
      if (key === 'categoryIds') {
        return (value as string[]).length > 0
      }
      if (key === 'uncategorizedOnly') {
        return value === true
      }
      return value !== null
    }),
  )

  async function fetchCategories() {
    loadingCategories.value = true
    try {
      const params = new URLSearchParams()
      if (selectedFolders.value.size > 0) {
        appendFolderParams(params, selectedFolders.value)
      }
      const query = params.toString()
      const data = await $fetch<{ categories: ImageCategoryInfo[] }>(
        query
          ? `${apiBase}/api/v1/categories?${query}`
          : `${apiBase}/api/v1/categories`,
      )
      categories.value = data.categories
    }
    catch {
      categories.value = []
    }
    finally {
      loadingCategories.value = false
    }
  }

  async function fetchFolders() {
    loadingFolders.value = true
    error.value = null
    try {
      const data = await $fetch<{ folders: FolderInfo[] }>(`${apiBase}/api/v1/folders`)
      folders.value = data.folders
      selectedFolders.value = new Set(data.folders.map(f => f.name))
    }
    catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load folders'
      folders.value = []
      images.value = []
      categories.value = []
      return
    }
    finally {
      loadingFolders.value = false
    }

    if (folders.value.length > 0) {
      void Promise.all([fetchImages(), fetchCategories()])
    }
  }

  async function fetchImages() {
    if (selectedFolders.value.size === 0) {
      images.value = []
      imagesError.value = null
      return
    }

    loadingImages.value = true
    imagesError.value = null
    try {
      const params = new URLSearchParams()
      appendFolderParams(params, selectedFolders.value)
      appendFilterParams(params, filters.value)

      const data = await $fetch<{ images: ImageEntry[], total: number }>(
        `${apiBase}/api/v1/images?${params.toString()}`,
      )
      images.value = data.images
    }
    catch (e) {
      imagesError.value = e instanceof Error ? e.message : 'Failed to load images'
      images.value = []
    }
    finally {
      loadingImages.value = false
    }
  }

  function isFolderSelected(name: string): boolean {
    return selectedFolders.value.has(name)
  }

  function toggleFolder(name: string) {
    const next = new Set(selectedFolders.value)
    if (next.has(name)) {
      next.delete(name)
    }
    else {
      next.add(name)
    }
    selectedFolders.value = next
    void Promise.all([fetchImages(), fetchCategories()])
  }

  function setFilter<K extends keyof ImageFilters>(key: K, value: ImageFilters[K]) {
    if (!captionsAvailable.value) {
      return
    }
    filters.value = { ...filters.value, [key]: value }
    void fetchImages()
  }

  function clearFilters() {
    filters.value = { ...EMPTY_IMAGE_FILTERS }
    void fetchImages()
  }

  function setPeopleRange(min: number | null, max: number | null) {
    if (!captionsAvailable.value) {
      return
    }
    filters.value = { ...filters.value, minPeople: min, maxPeople: max }
    void fetchImages()
  }

  function setQualityRange(min: number | null, max: number | null) {
    if (!captionsAvailable.value) {
      return
    }
    filters.value = { ...filters.value, minQualityScore: min, maxQualityScore: max }
    void fetchImages()
  }

  function toggleCategory(id: string) {
    if (!categoriesAvailable.value) {
      return
    }
    const current = new Set(filters.value.categoryIds)
    if (current.has(id)) {
      current.delete(id)
    }
    else {
      current.add(id)
    }
    filters.value = {
      ...filters.value,
      categoryIds: [...current],
      uncategorizedOnly: false,
    }
    void fetchImages()
  }

  function isCategorySelected(id: string): boolean {
    return filters.value.categoryIds.includes(id)
  }

  function setUncategorizedOnly(enabled: boolean) {
    if (!categoriesAvailable.value) {
      return
    }
    filters.value = {
      ...filters.value,
      uncategorizedOnly: enabled,
      categoryIds: enabled ? [] : filters.value.categoryIds,
    }
    void fetchImages()
  }

  function isDeleting(path: string): boolean {
    return deletingPaths.value.has(path)
  }

  async function deleteImage(path: string): Promise<boolean> {
    const label = path.split('/').pop() ?? path
    const confirmed = confirm(
      `Delete "${label}"?\n\nThis permanently removes the file from raw and processed folders and clears its metadata and category assignments.`,
    )
    if (!confirmed) {
      return false
    }

    const nextDeleting = new Set(deletingPaths.value)
    nextDeleting.add(path)
    deletingPaths.value = nextDeleting
    error.value = null

    try {
      await $fetch(imageDeleteUrl(path), { method: 'DELETE' })
      images.value = images.value.filter(image => image.path !== path)
      await Promise.all([fetchFolders(), fetchCategories()])
      return true
    }
    catch (e) {
      imagesError.value = e instanceof Error ? e.message : 'Failed to delete image'
      return false
    }
    finally {
      const done = new Set(deletingPaths.value)
      done.delete(path)
      deletingPaths.value = done
    }
  }

  const visibleCategories = computed(() =>
    categories.value.filter(category => category.image_count > 0),
  )

  watch(captionsAvailable, (available) => {
    if (!available && hasActiveFilters.value) {
      const hadCaptionFilters = filters.value.hasBride !== null
        || filters.value.hasGroom !== null
        || filters.value.hasOtherPeople !== null
        || filters.value.minPeople !== null
        || filters.value.maxPeople !== null
        || filters.value.analyzed !== null
        || filters.value.isBlur !== null
        || filters.value.minQualityScore !== null
        || filters.value.maxQualityScore !== null
      if (hadCaptionFilters) {
        filters.value = {
          ...filters.value,
          hasBride: null,
          hasGroom: null,
          hasOtherPeople: null,
          minPeople: null,
          maxPeople: null,
          analyzed: null,
          isBlur: null,
          minQualityScore: null,
          maxQualityScore: null,
        }
        void fetchImages()
      }
    }
  })

  watch(
    () => status.value?.categories_count,
    () => {
      void fetchCategories()
    },
  )

  onMounted(() => {
    void fetchFolders()
  })

  return {
    folders,
    selectedFolders,
    categories,
    visibleCategories,
    images,
    filters,
    hasActiveFilters,
    loadingFolders,
    loadingImages,
    loadingCategories,
    error,
    imagesError,
    mediaUrl,
    rawUrl,
    categoriesAvailable,
    fetchFolders,
    fetchImages,
    fetchCategories,
    isFolderSelected,
    toggleFolder,
    setFilter,
    clearFilters,
    setPeopleRange,
    setQualityRange,
    toggleCategory,
    isCategorySelected,
    setUncategorizedOnly,
    deleteImage,
    isDeleting,
  }
}
