import { describe, expect, it } from 'vitest'

import { assignDemoSlots, pickPreviewImage } from './layoutPreviewSlots'

describe('layoutPreviewSlots', () => {
  const paths = ['a.jpg', 'b.jpg', 'c.jpg', 'd.jpg']

  it('pickPreviewImage returns empty when no paths', () => {
    expect(pickPreviewImage([], 'key')).toBe('')
  })

  it('pickPreviewImage is stable for the same key and seed', () => {
    const a = pickPreviewImage(paths, 'layout:hero', 0)
    const b = pickPreviewImage(paths, 'layout:hero', 0)
    expect(a).toBe(b)
    expect(paths).toContain(a)
  })

  it('pickPreviewImage changes when seed changes', () => {
    const results = new Set(
      [0, 1, 2, 3, 4].map(seed => pickPreviewImage(paths, 'layout:hero', seed)),
    )
    expect(results.size).toBeGreaterThan(1)
  })

  it('assignDemoSlots fills every layout slot', () => {
    const layout = {
      id: 'test_layout',
      name: 'Test',
      description: '',
      slots: [
        { id: 'hero', label: 'Hero', aspect_hint: 'portrait' },
        { id: 'side', label: 'Side', aspect_hint: 'square' },
      ],
    }
    const slots = assignDemoSlots(layout, paths, 0)
    expect(Object.keys(slots).sort()).toEqual(['hero', 'side'])
    expect(paths).toContain(slots.hero)
    expect(paths).toContain(slots.side)
  })
})
