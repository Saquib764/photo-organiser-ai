import type { PhotobookPage } from '~/types/photobook'

/** Minimum time a page must be composing before another compose is allowed. */
export const COMPOSE_RETRY_AFTER_MS = 60_000

export function canComposePage(page: PhotobookPage, nowMs = Date.now()): boolean {
  if (page.status !== 'composing') {
    return true
  }
  if (!page.composing_started_at) {
    return true
  }
  const started = Date.parse(page.composing_started_at)
  if (Number.isNaN(started)) {
    return true
  }
  return nowMs - started >= COMPOSE_RETRY_AFTER_MS
}

export function anyPageCanCompose(pages: PhotobookPage[], nowMs = Date.now()): boolean {
  return pages.some(p => p.narrative.trim() && canComposePage(p, nowMs))
}
