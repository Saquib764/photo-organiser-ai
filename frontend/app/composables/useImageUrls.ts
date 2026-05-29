/** Build API URLs for processed thumbnails and raw workspace images. */
export function useImageUrls() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  function mediaUrl(path: string): string {
    const encoded = path.split('/').map(encodeURIComponent).join('/')
    return `${apiBase}/api/v1/media/${encoded}`
  }

  function rawUrl(path: string): string {
    const encoded = path.split('/').map(encodeURIComponent).join('/')
    return `${apiBase}/api/v1/raw/${encoded}`
  }

  return { apiBase, mediaUrl, rawUrl }
}
