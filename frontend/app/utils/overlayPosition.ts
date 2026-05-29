import type { TextAnchorX, TextAnchorY } from '~/types/pageLayoutRender'

const X_CLASSES: Record<TextAnchorX, string> = {
  left: 'justify-start',
  center: 'justify-center',
  right: 'justify-end',
}

const Y_CLASSES: Record<TextAnchorY, string> = {
  top: 'items-start',
  center: 'items-center',
  bottom: 'items-end',
}

/** Flex alignment classes for a 9-point text anchor inside a relative image frame. */
export function overlayPositionClasses(x: TextAnchorX, y: TextAnchorY): string {
  return `flex size-full p-3 ${Y_CLASSES[y]} ${X_CLASSES[x]}`
}

const SCRIM_CLASSES: Record<TextAnchorY, string> = {
  top: 'bg-gradient-to-b from-black/55 via-black/20 to-transparent',
  center: 'bg-black/25',
  bottom: 'bg-gradient-to-t from-black/55 via-black/20 to-transparent',
}

export function overlayScrimClass(y: TextAnchorY): string {
  return SCRIM_CLASSES[y]
}

/** Translucent pill behind on-image caption text (wraps copy only, not the frame). */
export const overlayTextPillClass =
  'inline-block max-w-full rounded-sm bg-white/85 px-3 py-1.5 shadow-sm backdrop-blur-[2px]'
