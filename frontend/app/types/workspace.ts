export interface LibraryFlags {
  image_found: boolean
  resize_complete: boolean
  people_extraction_complete: boolean
  has_analysed_color: boolean
  image_analysis_complete: boolean
  categorisation_complete: boolean
}

export type ProcessingPhase = 'resize' | 'faces' | 'palette' | 'analysis' | 'categorise'

export interface WorkspaceStatus {
  total_folder_raw: number
  total_images_raw: number
  total_images_processed: number
  flags: LibraryFlags
  processing_busy: boolean
  progress_total: number
  progress_completed: number
  progress_remaining: number
  processing_phase: ProcessingPhase | null
  resize_completed_count: number
  resize_total_count: number
  palette_completed_count: number
  palette_total_count: number
  analysis_completed_count: number
  analysis_total_count: number
  categorisation_completed_count: number
  categorisation_total_count: number
  face_completed_count: number
  face_total_count: number
  categories_count: number
  persons_count: number
  openai_configured: boolean
}

export interface WorkspaceStatusMessage {
  type: 'status'
  payload: WorkspaceStatus
}
