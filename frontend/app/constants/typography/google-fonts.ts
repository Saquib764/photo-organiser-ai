/**
 * Curated Google Fonts for photobook text.
 * Keep in sync with backend/app/typography/google_fonts.py
 */

export type GoogleFontCategory = 'cursive' | 'serif' | 'sans-serif' | 'monospace'

export interface GoogleFont {
  name: string
  family: string
  category: GoogleFontCategory
  role: string
  weights: readonly number[]
}

export const FONT_SCRIPT_DISPLAY = "'Great Vibes', cursive"
export const FONT_SERIF_DISPLAY = "'Cormorant Garamond', serif"
export const FONT_SERIF_EDITORIAL = "'Playfair Display', serif"
export const FONT_SANS_LABEL = "'Montserrat', sans-serif"
export const FONT_SANS_BODY = "'Lato', sans-serif"
export const FONT_SANS_EDITORIAL = "'Raleway', sans-serif"
export const FONT_SERIF_BODY = "'Lora', serif"
export const FONT_SERIF_NARRATIVE = "'Merriweather', serif"
export const FONT_MONO = "'Courier Prime', monospace"

export const GOOGLE_FONTS: readonly GoogleFont[] = [
  {
    name: 'Great Vibes',
    family: FONT_SCRIPT_DISPLAY,
    category: 'cursive',
    role: 'Script display — couple names, romantic titles',
    weights: [400],
  },
  {
    name: 'Cormorant Garamond',
    family: FONT_SERIF_DISPLAY,
    category: 'serif',
    role: 'Serif display — chapter headings, elegant titles',
    weights: [400, 500, 600],
  },
  {
    name: 'Playfair Display',
    family: FONT_SERIF_EDITORIAL,
    category: 'serif',
    role: 'Editorial display — formal section titles',
    weights: [400, 500, 600],
  },
  {
    name: 'Montserrat',
    family: FONT_SANS_LABEL,
    category: 'sans-serif',
    role: 'Sans label — dates, small caps, captions, badges',
    weights: [300, 400, 500],
  },
  {
    name: 'Lato',
    family: FONT_SANS_BODY,
    category: 'sans-serif',
    role: 'Sans body — readable supporting lines',
    weights: [300, 400, 700],
  },
  {
    name: 'Raleway',
    family: FONT_SANS_EDITORIAL,
    category: 'sans-serif',
    role: 'Sans editorial — airy labels and subtitles',
    weights: [400, 500, 600],
  },
  {
    name: 'Lora',
    family: FONT_SERIF_BODY,
    category: 'serif',
    role: 'Serif body — warm narrative paragraphs',
    weights: [400, 500],
  },
  {
    name: 'Merriweather',
    family: FONT_SERIF_NARRATIVE,
    category: 'serif',
    role: 'Serif narrative — longer story text',
    weights: [400, 700],
  },
  {
    name: 'Courier Prime',
    family: FONT_MONO,
    category: 'monospace',
    role: 'Monospace — dates, codes, typewriter accents',
    weights: [400],
  },
] as const

export const ALLOWED_FONT_FAMILIES: ReadonlySet<string> = new Set(
  GOOGLE_FONTS.map((font) => font.family),
)

const FONT_BY_NAME = new Map(
  GOOGLE_FONTS.map((font) => [font.name.toLowerCase(), font.family]),
)

export function coerceFontFamily(
  value: string,
  fallback: string = FONT_SANS_LABEL,
): string {
  const stripped = value.trim()
  if (ALLOWED_FONT_FAMILIES.has(stripped)) {
    return stripped
  }
  const lowered = stripped.toLowerCase().replace(/['"]/g, '')
  for (const [name, family] of FONT_BY_NAME) {
    if (lowered.includes(name)) {
      return family
    }
  }
  return fallback
}

export function googleFontsStylesheetUrl(): string {
  const parts = GOOGLE_FONTS.map((font) => {
    const encoded = encodeURIComponent(font.name)
    if (font.weights.length === 1) {
      return `family=${encoded}`
    }
    const axis = font.weights.join(';')
    return `family=${encoded}:wght@${axis}`
  })
  return `https://fonts.googleapis.com/css2?${parts.join('&')}&display=swap`
}
