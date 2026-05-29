import type { LayoutColorGuidance } from '~/types/photobook'

export const HINT_SCRIPT_DISPLAY =
  'Dark warm brown for script display names and titles; high contrast on light backgrounds'
export const HINT_SANS_LABEL =
  'Dark warm brown for small sans-serif labels (dates, taglines); same hue family as display text'
export const HINT_SANS_BODY =
  'Dark warm brown for body copy and captions; readable at small sizes on white or blush'
export const HINT_BADGE_TEXT =
  'Dark warm brown for short badge headline on a near-white circular overlay'

export const IMAGE_LED_BACKGROUND: LayoutColorGuidance = {
  page_background:
    'Neutral sheet or color pulled from the primary image palette; should not compete with photography',
}

export const BOHO_SPLIT_COVER_COLORS: LayoutColorGuidance = {
  page_background: 'Warm cream off-white sheet; airy editorial feel',
  text_primary: 'Dark warm brown for script couple names; strongest contrast on the page',
  text_secondary: 'Dark warm brown for small caps heading and subtitle',
  decorative: 'Muted rose-tan botanical line art in corners when present; low contrast framing only',
}

export const WEDDING_COVER_COLORS: LayoutColorGuidance = {
  page_background: 'Clean near-white sheet; bright and airy so photos and typography stand out',
  text_primary: 'Dark warm brown for script couple names; strongest contrast on the page',
  text_secondary: 'Dark warm brown for date and tagline; works at small uppercase sizes',
  accent: 'Soft dusty blush bar along the bottom edge; subtle warmth, not dominant',
  decorative:
    'Muted rose-tan ornamental side borders and hairline dividers; low contrast, framing only',
}

export const WEDDING_STORY_LEFT_COLORS: LayoutColorGuidance = {
  page_background: 'Soft blush pink sheet; warm and romantic, lighter than accent tones',
  content_surfaces: 'White arch/caption well; crisp contrast for centered copy',
  text_primary: 'Dark warm brown script heading on blush background',
  text_secondary: 'Dark warm brown sans caption inside the white arch',
}

export const WEDDING_STORY_RIGHT_COLORS: LayoutColorGuidance = {
  page_background: 'Clean white sheet; neutral so photos carry color',
  text_primary: 'Dark warm brown script couple names at the foot of the page',
}

export const WEDDING_WHITE_SHEET_COLORS: LayoutColorGuidance = {
  page_background: 'Clean white sheet; neutral gallery feel',
  text_primary: 'Dark warm brown for script titles when present',
  text_secondary: 'Dark warm brown for footer captions and labels',
}

export const WEDDING_EDITORIAL_COLORS: LayoutColorGuidance = {
  page_background: 'Clean white sheet with generous margins around photos',
  text_primary: 'Dark warm brown for script headings',
  text_secondary: 'Dark warm brown for body copy; left-aligned, comfortable line length',
}

export const WEDDING_FULL_BLEED_COLORS: LayoutColorGuidance = {
  page_background: 'Full-bleed photo; no separate sheet color',
  overlay: 'Near-white semi-opaque circular badge (~92% opacity) with soft shadow',
  text_primary: 'Dark warm brown badge text; must read on the white badge, not on the photo',
}

export const WEDDING_BACK_COVER_COLORS: LayoutColorGuidance = {
  page_background: 'Clean white closing sheet; calm and minimal',
  text_primary: 'Dark warm brown script couple names',
  text_secondary: 'Dark warm brown thank-you message; slightly lighter typographic weight',
  decorative: 'Muted rose-tan hairline ring around the circular portrait',
}

export const WEDDING_BACK_COVER_ORNATE_COLORS: LayoutColorGuidance = {
  page_background: 'Clean near-white closing sheet; bright and airy',
  text_primary: 'Dark warm brown script couple names; strongest contrast on the page',
  text_secondary: 'Dark warm brown thank-you and date; works at small uppercase sizes',
  accent: 'Soft dusty blush bar along the bottom edge; subtle warmth, not dominant',
  decorative:
    'Muted rose-tan ornamental side borders and hairline dividers; low contrast, framing only',
}

export const WEDDING_BACK_COVER_BOHO_COLORS: LayoutColorGuidance = {
  page_background: 'Warm cream off-white closing sheet; airy editorial feel',
  text_primary: 'Dark warm brown script couple names; strongest contrast on the page',
  text_secondary: 'Dark warm brown small caps label and thank-you body',
  decorative: 'Soft shadows on overlapping rounded photos; low contrast framing only',
}

export const WEDDING_BACK_COVER_BLEED_COLORS: LayoutColorGuidance = {
  page_background: 'Full-bleed photo; no separate sheet color',
  overlay: 'Near-white footer band (~25% page height) for closing copy',
  text_primary: 'Dark warm brown script couple names on the footer band',
  text_secondary: 'Dark warm brown thank-you message on the footer band',
}
