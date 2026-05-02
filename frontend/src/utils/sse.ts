export const SSE_EVENT_TOKEN = 'token'
export const SSE_EVENT_SOURCES = 'sources'
export const SSE_EVENT_DONE = 'done'

export interface SSECallbacks {
  onToken: (token: string) => void
  onSources: (sources: { content: string; source: string }[]) => void
  onDone: () => void
  onError: (error: Error) => void
}

export function parseSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  callbacks: SSECallbacks,
): void {
  const decoder = new TextDecoder()
  let buffer = ''
  let currentEvent = ''

  const processLines = () => {
    void (async () => {
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            callbacks.onDone()
            break
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              const rawData = line.slice(6)
              try {
                const data = JSON.parse(rawData) as Record<string, unknown>
                switch (currentEvent) {
                  case SSE_EVENT_TOKEN:
                    callbacks.onToken(data.token as string)
                    break
                  case SSE_EVENT_SOURCES:
                    callbacks.onSources(data.sources as { content: string; source: string }[])
                    break
                  case SSE_EVENT_DONE:
                    callbacks.onDone()
                    break
                }
              } catch {
                // skip malformed JSON lines
              }
            }
          }
        }
      } catch (error) {
        callbacks.onError(error instanceof Error ? error : new Error(String(error)))
      }
    })()
  }

  processLines()
}
