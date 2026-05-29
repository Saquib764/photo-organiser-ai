import type { LayoutDefinition } from '~/types/photobook'
import type { PageLayoutCategory, PageLayoutDefinition } from '~/types/pageLayoutRender'

export type {
  PageLayoutCategory,
  PageLayoutDefinition,
  RenderNode,
} from '~/types/pageLayoutRender'

const jsonModules = import.meta.glob<PageLayoutDefinition[]>('./*.json', {
  eager: true,
  import: 'default',
})

function fileKeyFromPath(path: string): string {
  return path.replace(/^\.\//, '').replace(/\.json$/, '')
}

/** Each key is a library filename without `.json` (e.g. `photo-grids`). */
export const PAGE_LAYOUT_LIBRARY_FILES = Object.fromEntries(
  Object.entries(jsonModules).map(([path, layouts]) => [
    fileKeyFromPath(path),
    layouts,
  ]),
) as Record<string, PageLayoutDefinition[]>

export type PageLayoutLibraryFile = keyof typeof PAGE_LAYOUT_LIBRARY_FILES

export const PAGE_LAYOUTS: PageLayoutDefinition[] = Object.values(
  PAGE_LAYOUT_LIBRARY_FILES,
).flat()

const _byId = new Map(PAGE_LAYOUTS.map(layout => [layout.id, layout]))

if (import.meta.dev && _byId.size !== PAGE_LAYOUTS.length) {
  throw new Error('Duplicate page layout ids in PAGE_LAYOUTS')
}

export function getPageLayout(layoutId: string): PageLayoutDefinition | undefined {
  return _byId.get(layoutId)
}

export function layoutsFromFile(file: PageLayoutLibraryFile): PageLayoutDefinition[] {
  const layouts = PAGE_LAYOUT_LIBRARY_FILES[file]
  if (!layouts) {
    throw new Error(`Unknown page layout library file: ${String(file)}`)
  }
  return layouts
}

function byCategory(category: PageLayoutCategory): PageLayoutDefinition[] {
  return PAGE_LAYOUTS.filter(layout => layout.category === category)
}

export const PAGE_LAYOUT_CATEGORIES = {
  grids: byCategory('grids'),
  cover: byCategory('cover'),
  wedding: byCategory('wedding'),
} as const

/** Catalogue fields for API parity checks and layout pickers (no render tree). */
export function toLayoutDefinition(layout: PageLayoutDefinition): LayoutDefinition {
  const { category: _category, render: _render, ...catalog } = layout
  return catalog
}

export const PAGE_LAYOUT_CATALOG: LayoutDefinition[] = PAGE_LAYOUTS.map(toLayoutDefinition)
