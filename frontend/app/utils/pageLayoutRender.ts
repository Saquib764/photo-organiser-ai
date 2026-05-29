import { getPageLayout } from '~/constants/pageLayouts'

export function canRenderPageLayout(layoutId: string | null | undefined): boolean {
  return !!layoutId && !!getPageLayout(layoutId)
}
