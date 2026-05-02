import { useEffect, useRef, useCallback } from 'react'
import { useAppStore } from '@/stores/appStore'
import { ragApi } from '@/services/ragApi'
import { RAG_STATUS_POLL_INTERVAL } from '@/utils/constants'

export function useRAGStatus() {
  const ragStatus = useAppStore((s) => s.ragStatus)
  const setRagStatus = useAppStore((s) => s.setRagStatus)
  const isModelLoading = useAppStore((s) => s.isModelLoading)
  const setModelLoading = useAppStore((s) => s.setModelLoading)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchStatus = useCallback(async () => {
    try {
      const status = await ragApi.getStatus()
      setRagStatus(status)
      if (isModelLoading && status.engine_loaded) {
        setModelLoading(false)
      }
    } catch {
      // silently ignore status fetch errors
    }
  }, [setRagStatus, isModelLoading, setModelLoading])

  useEffect(() => {
    void fetchStatus()

    intervalRef.current = setInterval(() => {
      void fetchStatus()
    }, RAG_STATUS_POLL_INTERVAL)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetchStatus])

  const loadModel = useCallback(
    async (
      modelKey: string,
      options?: {
        modelDir?: string
        useReranker?: boolean
        rerankerModel?: string
        rerankerTopK?: number
        initialRetrievalK?: number
      },
    ) => {
      setModelLoading(true)
      try {
        await ragApi.loadModel({
          model_key: modelKey,
          model_dir: options?.modelDir,
          use_reranker: options?.useReranker,
          reranker_model: options?.rerankerModel,
          reranker_top_k: options?.rerankerTopK,
          initial_retrieval_k: options?.initialRetrievalK,
        })
      } catch (error) {
        setModelLoading(false)
        throw error
      }
    },
    [setModelLoading],
  )

  const unloadModel = useCallback(async () => {
    await ragApi.unloadModel()
    await fetchStatus()
  }, [fetchStatus])

  return {
    ragStatus,
    isModelLoading,
    loadModel,
    unloadModel,
    refreshStatus: fetchStatus,
  }
}
