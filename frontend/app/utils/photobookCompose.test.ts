import { describe, expect, it } from 'vitest'
import type { PhotobookPage } from '~/types/photobook'
import { canComposePage, COMPOSE_RETRY_AFTER_MS } from './photobookCompose'

function page(overrides: Partial<PhotobookPage> = {}): PhotobookPage {
  return {
    id: 'p1',
    title: 'Page',
    narrative: 'Story',
    layout_id: '',
    slots: {},
    palette_colors: [],
    background_color: null,
    image_border_radius: 0,
    status: 'draft',
    composing_started_at: null,
    composed_at: null,
    error_message: null,
    ...overrides,
  }
}

describe('canComposePage', () => {
  it('allows compose when not composing', () => {
    expect(canComposePage(page())).toBe(true)
  })

  it('blocks compose within one minute', () => {
    const now = Date.now()
    const p = page({
      status: 'composing',
      composing_started_at: new Date(now - 30_000).toISOString(),
    })
    expect(canComposePage(p, now)).toBe(false)
  })

  it('allows recompose after one minute', () => {
    const now = Date.now()
    const p = page({
      status: 'composing',
      composing_started_at: new Date(now - COMPOSE_RETRY_AFTER_MS - 1).toISOString(),
    })
    expect(canComposePage(p, now)).toBe(true)
  })

  it('allows recompose when composing without timestamp', () => {
    expect(canComposePage(page({ status: 'composing', composing_started_at: null }))).toBe(true)
  })
})
