import type { LayoutDefinition } from '~/types/photobook'

function hashString(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) | 0
  }
  return Math.abs(hash)
}

/** Stable pseudo-random image pick per layout slot (changes when seed changes). */
export function pickPreviewImage(
  imagePaths: string[],
  key: string,
  seed = 0,
): string {
  if (!imagePaths.length) {
    return ''
  }
  const idx = hashString(`${seed}:${key}`) % imagePaths.length
  return imagePaths[idx] ?? ''
}

export function assignDemoSlots(
  layout: LayoutDefinition,
  imagePaths: string[],
  seed = 0,
): Record<string, string> {
  const slots: Record<string, string> = {}
  for (const slot of layout.slots ?? []) {
    const path = pickPreviewImage(imagePaths, `${layout.id}:${slot.id}`, seed)
    if (path) {
      slots[slot.id] = path
    }
  }
  return slots
}
