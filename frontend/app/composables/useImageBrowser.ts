import type { FolderInfo, ImageCategoryInfo, ImageEntry, ImageFilters } from '~/types/images'
import { EMPTY_IMAGE_FILTERS, folderApiToken, IMAGE_PAGE_SIZE, type ImageListResponse } from '~/types/images'

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
  for (const id of filters.personIds) {
    params.append('person_ids', id)
  }
}

function appendFolderParams(params: URLSearchParams, folderNames: Set<string>) {
  for (const name of folderNames) {
    params.append('folders', folderApiToken(name))
  }
}

export function useImageBrowser() {
  const { apiBase, mediaUrl, rawUrl } = useImageUrls()
  const { captionsAvailable, peopleAvailable, status } = useWorkspaceStatusDisplay()

  const folders = ref<FolderInfo[]>([])
  const selectedFolders = ref<Set<string>>(new Set())
  const categories = ref<ImageCategoryInfo[]>([])

  /** True when image_categories.json has at least one category (from API, not WebSocket). */
  const categoriesAvailable = computed(() => categories.value.length > 0)
  const images = ref<ImageEntry[]>([])
  const imagesTotal = ref(0)
  const hasMoreImages = ref(false)
  const filters = ref<ImageFilters>({ ...EMPTY_IMAGE_FILTERS })
  const loadingFolders = ref(false)
  const loadingImages = ref(false)
  const loadingMoreImages = ref(false)
  const loadingCategories = ref(false)
  const deletingPaths = ref<Set<string>>(new Set())
  /** Folder list fetch failures (sidebar). */
  const error = ref<string | null>(null)
  /** Image list fetch failures (grid); does not clear folders. */
  const imagesError = ref<string | null>(null)

  let fetchGeneration = 0

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
      if (key === 'personIds') {
        return (value as string[]).length > 0
      }
      return value !== null
    }),
  )

  function buildImageQueryParams(offset: number, limit: number): URLSearchParams {
    const params = new URLSearchParams()
    appendFolderParams(params, selectedFolders.value)
    appendFilterParams(params, filters.value)
    params.set('offset', String(offset))
    params.set('limit', String(limit))
    return params
  }

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
      imagesTotal.value = 0
      hasMoreImages.value = false
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

  async function fetchImagePage(reset: boolean, limit = IMAGE_PAGE_SIZE) {
    if (selectedFolders.value.size === 0) {
      images.value = []
      imagesTotal.value = 0
      hasMoreImages.value = false
      imagesError.value = null
      return
    }

    const generation = ++fetchGeneration
    const offset = reset ? 0 : images.value.length

    if (reset) {
      loadingImages.value = true
      imagesError.value = null
      images.value = []
      imagesTotal.value = 0
      hasMoreImages.value = false
    }
    else {
      loadingMoreImages.value = true
    }

    try {
      const data = await $fetch<ImageListResponse>(
        `${apiBase}/api/v1/images?${buildImageQueryParams(offset, limit).toString()}`,
      )
      if (generation !== fetchGeneration) {
        return
      }

      if (reset) {
        images.value = data.images
      }
      else {
        images.value = [...images.value, ...data.images]
      }
      imagesTotal.value = data.total
      hasMoreImages.value = data.has_more
    }
    catch (e) {
      if (generation !== fetchGeneration) {
        return
      }
      imagesError.value = e instanceof Error ? e.message : 'Failed to load images'
      if (reset) {
        images.value = []
        imagesTotal.value = 0
        hasMoreImages.value = false
      }
    }
    finally {
      if (generation === fetchGeneration) {
        if (reset) {
          loadingImages.value = false
        }
        else {
          loadingMoreImages.value = false
        }
      }
    }
  }

  async function fetchImages(options?: { limit?: number }) {
    await fetchImagePage(true, options?.limit ?? IMAGE_PAGE_SIZE)
  }

  async function loadMoreImages() {
    if (
      selectedFolders.value.size === 0
      || !hasMoreImages.value
      || loadingImages.value
      || loadingMoreImages.value
    ) {
      return
    }
    await fetchImagePage(false)
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

  function togglePerson(id: string) {
    if (!peopleAvailable.value) {
      return
    }
    const current = new Set(filters.value.personIds)
    if (current.has(id)) {
      current.delete(id)
    }
    else {
      current.add(id)
    }
    filters.value = { ...filters.value, personIds: [...current] }
    void fetchImages()
  }

  function isPersonSelected(id: string): boolean {
    return filters.value.personIds.includes(id)
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
      imagesTotal.value = Math.max(0, imagesTotal.value - 1)
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

  watch(peopleAvailable, (available) => {
    if (!available && filters.value.personIds.length > 0) {
      filters.value = { ...filters.value, personIds: [] }
      void fetchImages()
    }
  })

  onMounted(() => {
    void fetchFolders()
  })

  return {
    folders,
    selectedFolders,
    categories,
    visibleCategories,
    images,
    imagesTotal,
    hasMoreImages,
    filters,
    hasActiveFilters,
    loadingFolders,
    loadingImages,
    loadingMoreImages,
    loadingCategories,
    error,
    imagesError,
    mediaUrl,
    rawUrl,
    categoriesAvailable,
    peopleAvailable,
    fetchFolders,
    fetchImages,
    loadMoreImages,
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
    togglePerson,
    isPersonSelected,
    deleteImage,
    isDeleting,
  }
}
