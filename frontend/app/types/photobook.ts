export type PhotobookPageStatus = 'draft' | 'composing' | 'ready' | 'error'
export type ChatRole = 'user' | 'assistant'

export type PageRole = 'cover' | 'middle' | 'back'

export interface LayoutSlotDefinition {
  id: string
  label: string
  aspect_hint: string
}

export interface LayoutColorGuidance {
  page_background?: string
  content_surfaces?: string
  text_primary?: string
  text_secondary?: string
  accent?: string
  decorative?: string
  overlay?: string
}

export interface LayoutTextSlotDefinition {
  id: string
  label: string
  default_text: string
  color_hint: string
  default_font_family: string
  default_font_size: string
  default_font_weight: string
  default_letter_spacing: string
  default_text_align: string
  default_text_transform: string
}

export interface TextSlotValue {
  text: string
  color: string
  font_family: string
  font_size: string
  font_weight: string
  letter_spacing: string
  text_align: string
  text_transform: string
}

export interface LayoutDefinition {
  id: string
  name: string
  description: string
  slots: LayoutSlotDefinition[]
  text_slots?: LayoutTextSlotDefinition[]
  color_guidance?: LayoutColorGuidance | null
  page_role?: PageRole | null
}

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  created_at: string
}

/** Pan position for object-cover images (CSS object-position percentages). */
export interface SlotOffset {
  x: number
  y: number
}

export interface PhotobookPage {
  id: string
  title: string
  narrative: string
  layout_id: string
  categories?: string[]
  slots: Record<string, string>
  text_slots?: Record<string, TextSlotValue>
  slot_offsets?: Record<string, SlotOffset>
  palette_colors: string[]
  background_color: string | null
  image_border_radius: number
  status: PhotobookPageStatus
  composing_started_at?: string | null
  composed_at: string | null
  layout_error?: string | null
  error_message: string | null
  extra_images?: string[]
}

export interface PhotobookDocument {
  title: string
  chat: ChatMessage[]
  pages: PhotobookPage[]
}

export interface PhotobookResponse {
  document: PhotobookDocument
  layouts: LayoutDefinition[]
}

export interface PhotobookChatResponse extends PhotobookResponse {
  assistant_message: string
}

export interface UChatMessageItem {
  id: string
  role: ChatRole
  parts: Array<{ type: 'text', text: string }>
}

export function toUChatMessages(chat: ChatMessage[]): UChatMessageItem[] {
  return chat.map(msg => ({
    id: msg.id,
    role: msg.role,
    parts: [{ type: 'text' as const, text: msg.content }],
  }))
}
