import type { WorkspaceStatus, WorkspaceStatusMessage } from '~/types/workspace'
import { resolveWsUrl } from '~/utils/wsUrl'

export type WorkspaceConnectionState = 'connecting' | 'open' | 'closed'

let socket: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let initialized = false
const statusWaitQueue: Array<() => void> = []

const RECONNECT_MS = 3000

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

function scheduleReconnect(connect: () => void) {
  clearReconnectTimer()
  reconnectTimer = setTimeout(connect, RECONNECT_MS)
}

export function useWorkspaceSocket() {
  const config = useRuntimeConfig()
  const status = useState<WorkspaceStatus | null>('workspace-status', () => null)

  function handleMessage(event: MessageEvent<string>) {
    let data: WorkspaceStatusMessage
    try {
      data = JSON.parse(event.data) as WorkspaceStatusMessage
    }
    catch {
      return
    }

    if (data.type === 'status' && data.payload) {
      status.value = data.payload
      statusWaitQueue.shift()?.()
    }
  }
  const connectionState = useState<WorkspaceConnectionState>(
    'workspace-connection-state',
    () => 'closed',
  )

  function connect() {
    if (!import.meta.client) {
      return
    }

    if (
      socket
      && (socket.readyState === WebSocket.OPEN
        || socket.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

    const wsBase = config.public.wsUrl || config.public.apiBase
    const url = resolveWsUrl(wsBase)
    connectionState.value = 'connecting'

    socket = new WebSocket(url)

    // Attach handlers before the connection can open so the initial status
    // message from the server is not dropped.
    socket.onmessage = handleMessage

    socket.onopen = () => {
      connectionState.value = 'open'
    }

    socket.onerror = () => {
      connectionState.value = 'closed'
    }

    socket.onclose = () => {
      connectionState.value = 'closed'
      socket = null
      scheduleReconnect(connect)
    }
  }

  function disconnect() {
    clearReconnectTimer()
    if (socket) {
      socket.onclose = null
      socket.close()
      socket = null
    }
    connectionState.value = 'closed'
  }

  function requestStatus(options?: { discover?: boolean }): Promise<void> {
    if (socket?.readyState !== WebSocket.OPEN) {
      return Promise.resolve()
    }

    const discover = options?.discover ?? false

    return new Promise((resolve) => {
      const timeout = window.setTimeout(() => {
        const index = statusWaitQueue.indexOf(done)
        if (index !== -1) {
          statusWaitQueue.splice(index, 1)
        }
        resolve()
      }, 60_000)

      function done() {
        window.clearTimeout(timeout)
        resolve()
      }

      statusWaitQueue.push(done)
      socket!.send(JSON.stringify({ type: 'request_status', discover }))
    })
  }

  function startProcessing() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'start_processing' }))
    }
  }

  function startAnalysis() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'start_analysis' }))
    }
  }

  function rerunAnalysis() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'rerun_analysis' }))
    }
  }

  function startCategorisation() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'start_categorisation' }))
    }
  }

  function rerunCategorisation() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'rerun_categorisation' }))
    }
  }

  function startPaletteExtraction() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'start_palette_extraction' }))
      // Request status again shortly after the server accepts the job.
      window.setTimeout(() => requestStatus(), 250)
    }
  }

  onMounted(() => {
    if (!initialized) {
      initialized = true
      connect()
    }
  })

  return {
    status,
    connectionState,
    connect,
    disconnect,
    requestStatus,
    startProcessing,
    startPaletteExtraction,
    startAnalysis,
    rerunAnalysis,
    startCategorisation,
    rerunCategorisation,
  }
}
