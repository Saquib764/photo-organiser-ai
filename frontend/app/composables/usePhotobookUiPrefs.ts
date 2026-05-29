export type PhotobookAspectRatio = '9:16' | '1:1' | '16:9'

export function usePhotobookUiPrefs() {
  const aspectRatio = useState<PhotobookAspectRatio>('photobook-aspect-ratio', () => '16:9')

  const aspectItems: { label: string; value: PhotobookAspectRatio }[] = [
    { label: '9:16', value: '9:16' },
    { label: '1:1', value: '1:1' },
    { label: '16:9', value: '16:9' },
  ]

  return { aspectRatio, aspectItems }
}

