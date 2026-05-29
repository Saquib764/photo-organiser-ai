import type { LayoutColorGuidance, LayoutDefinition } from '~/types/photobook'

export type PageLayoutCategory = 'grids' | 'cover' | 'wedding'

export type ImageBorderRadiusMode = 'inherit' | 'none' | 'arch' | 'full'

export type ThemeBackgroundKey = 'white' | 'blush' | 'accentBar'

export type TextAnchorX = 'left' | 'center' | 'right'

export type TextAnchorY = 'top' | 'center' | 'bottom'

export interface ImageTextOverlay {
  textSlotId: string
  x: TextAnchorX
  y: TextAnchorY
  when?: 'always' | 'if_text'
  class?: string
  scrim?: boolean
}

export interface RenderImageNode {
  type: 'image'
  slotId: string
  placeholder?: string
  dimmed?: boolean
  borderRadius?: ImageBorderRadiusMode
  overlay?: ImageTextOverlay
}

export interface RenderTextNode {
  type: 'text'
  slotId: string
  multiline?: boolean
  class?: string
  when?: 'always' | 'if_text'
}

export interface RenderDividerNode {
  type: 'divider'
  class?: string
}

export interface RenderOrnamentNode {
  type: 'ornament'
  variant: 'wedding_side_borders' | 'accent_bar' | 'arch_caption_well' | 'hairline'
}

export interface RenderBoxNode {
  type: 'box'
  class?: string
  style?: Record<string, string>
  themeBackground?: ThemeBackgroundKey
  flex?: number | string
  aspect?: string
  imageFrame?: 'arch'
  children?: RenderNode[]
}

export interface RenderStackNode {
  type: 'stack'
  direction?: 'row' | 'col'
  gap?: number | string
  class?: string
  themeBackground?: ThemeBackgroundKey
  children: RenderNode[]
}

export interface RenderGridNode {
  type: 'grid'
  cols?: number
  class?: string
  gap?: number | string
  templateColumns?: string
  templateRows?: string
  children: RenderNode[]
}

export interface RenderAbsoluteNode {
  type: 'absolute'
  class?: string
  children: RenderNode[]
}

export interface RenderForeachNode {
  type: 'foreach'
  keys: string[]
  class?: string
  child: RenderNode
}

export interface RenderMosaicNode {
  type: 'mosaic'
  class?: string
  gap?: string
  templateColumns?: string
  templateRows?: string
  cells: Array<{ slotId: string, gridColumn: string }>
}

export type RenderNode =
  | RenderImageNode
  | RenderTextNode
  | RenderDividerNode
  | RenderOrnamentNode
  | RenderBoxNode
  | RenderStackNode
  | RenderGridNode
  | RenderAbsoluteNode
  | RenderForeachNode
  | RenderMosaicNode

export interface PageLayoutDefinition extends LayoutDefinition {
  category: PageLayoutCategory
  color_guidance?: LayoutColorGuidance | null
  render: RenderNode
}
