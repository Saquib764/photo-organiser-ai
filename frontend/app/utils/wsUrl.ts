const WS_PATH = '/ws'

export function resolveWsUrl(apiOrWsBase: string): string {
  const trimmed = apiOrWsBase.replace(/\/$/, '')
  if (trimmed.startsWith('ws://') || trimmed.startsWith('wss://')) {
    return trimmed.endsWith(WS_PATH) ? trimmed : `${trimmed}${WS_PATH}`
  }

  const url = new URL(trimmed)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  url.pathname = WS_PATH
  url.search = ''
  url.hash = ''
  return url.toString()
}
