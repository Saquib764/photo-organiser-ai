export interface PersonSummary {
  id: string
  name: string
  description: string
  thumbnail_url: string
  face_count: number
  image_count: number
}

export interface PersonListResponse {
  persons: PersonSummary[]
}

export interface PersonUpdateRequest {
  name?: string
  description?: string
}

export interface PersonDeleteResponse {
  id: string
  removed_from_metadata: number
}
