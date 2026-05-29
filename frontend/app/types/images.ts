export interface FolderInfo {
  name: string
  image_count: number
}

export interface ImageCategoryInfo {
  id: string
  description: string
  image_count: number
}

export interface ImageEntry {
  path: string
  folder: string
  category_id: string | null
  caption: string
  number_of_people: number
  has_bride: boolean
  has_groom: boolean
  has_other_people: boolean
  is_blur: boolean
  quality_score: number
  analyzed: boolean
}

export interface ImageFilters {
  hasBride: boolean | null
  hasGroom: boolean | null
  hasOtherPeople: boolean | null
  minPeople: number | null
  maxPeople: number | null
  analyzed: boolean | null
  isBlur: boolean | null
  minQualityScore: number | null
  maxQualityScore: number | null
  categoryIds: string[]
  uncategorizedOnly: boolean
}

export const EMPTY_IMAGE_FILTERS: ImageFilters = {
  hasBride: null,
  hasGroom: null,
  hasOtherPeople: null,
  minPeople: null,
  maxPeople: null,
  analyzed: null,
  isBlur: null,
  minQualityScore: null,
  maxQualityScore: null,
  categoryIds: [],
  uncategorizedOnly: false,
}

export type TriStateFilter = boolean | null

export interface FolderListResponse {
  folders: FolderInfo[]
}

export interface ImageListResponse {
  images: ImageEntry[]
  total: number
}

/** API token for images directly under raw/ (folder name is empty). */
export const ROOT_FOLDER_TOKEN = '__root__'

export function folderApiToken(name: string): string {
  return name === '' ? ROOT_FOLDER_TOKEN : name
}

export function folderDisplayName(name: string): string {
  return name === '' ? 'Root' : name
}

/** Button label for who-is-in-photo tri-state filters. */
export function whoInPhotoLabel(role: string, value: TriStateFilter): string {
  if (value === true) {
    return `With ${role}`
  }
  if (value === false) {
    return `Without ${role}`
  }
  return role
}

export function cycleTriState(value: TriStateFilter): TriStateFilter {
  if (value === null) {
    return true
  }
  if (value === true) {
    return false
  }
  return null
}

/** Human-readable label from a story category id (e.g. couple_portraits). */
export function categoryDisplayLabel(id: string): string {
  return id
    .split('_')
    .filter(Boolean)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
