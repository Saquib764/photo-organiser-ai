import type {
  LayoutTextSlotDefinition,
  TextSlotValue,
} from '~/types/photobook'
import type { PageLayoutDefinition } from '~/types/pageLayoutRender'

import { coerceFontFamily } from '~/constants/typography/google-fonts'
import { WEDDING_THEME } from '~/constants/photobook/theme'

export { WEDDING_THEME } from '~/constants/photobook/theme'

function textSlotFromDefinition(slot: LayoutTextSlotDefinition): TextSlotValue {
  return {
    text: slot.default_text,
    color: '',
    font_family: slot.default_font_family,
    font_size: slot.default_font_size,
    font_weight: slot.default_font_weight,
    letter_spacing: slot.default_letter_spacing,
    text_align: slot.default_text_align,
    text_transform: slot.default_text_transform,
  }
}

/** Default text slots for layout library demo previews only. */
export function defaultTextSlotsFromLayout(
  layout: PageLayoutDefinition,
): Record<string, TextSlotValue> {
  const merged: Record<string, TextSlotValue> = {}
  for (const slot of layout.text_slots ?? []) {
    merged[slot.id] = textSlotFromDefinition(slot)
  }
  return merged
}

export function resolveTextSlotColor(value: TextSlotValue): string {
  if (value.color) {
    return value.color
  }
  return WEDDING_THEME.brown
}

export function textSlotStyle(value: TextSlotValue): Record<string, string> {
  return {
    color: resolveTextSlotColor(value),
    fontFamily: coerceFontFamily(value.font_family),
    fontSize: value.font_size,
    fontWeight: value.font_weight,
    letterSpacing: value.letter_spacing,
    textAlign: value.text_align,
    textTransform: value.text_transform,
  }
}
