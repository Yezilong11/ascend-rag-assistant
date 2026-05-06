import React, { useCallback, useEffect, useState } from 'react'
import { message } from 'antd'
import { useRAGStatus } from '@/hooks/useRAGStatus'
import { knowledgeBaseApi } from '@/services/knowledgeBaseApi'
import EngineControl from '@/components/settings/EngineControl'
import KnowledgeBasePanel from '@/components/knowledge/KnowledgeBasePanel'
import type { KnowledgeBaseStats, ModelLoadRequest } from '@/types/rag'

const SettingsPage: React.FC = () => {
  const { ragStatus, isModelLoading, loadModel, unloadModel, refreshStatus } = useRAGStatus()
  const [kbStats, setKbStats] = useState<KnowledgeBaseStats | null>(null)

  useEffect(() => {
    knowledgeBaseApi
      .getStats()
      .then(setKbStats)
      .catch(() => {})
  }, [])

  const handleLoad = useCallback(
    async (request: ModelLoadRequest) => {
      try {
        await loadModel(request.model_key, {
          modelDir: request.model_dir,
          useReranker: request.use_reranker,
          rerankerModel: request.reranker_model,
          rerankerTopK: request.reranker_top_k,
          initialRetrievalK: request.initial_retrieval_k,
        })
        message.success('模型加载请求已发送，请等待加载完成')
      } catch (error) {
        message.error((error as Error).message)
      }
    },
    [loadModel],
  )

  const handleUnload = useCallback(async () => {
    try {
      await unloadModel()
      message.success('模型已卸载')
    } catch (error) {
      message.error((error as Error).message)
    }
  }, [unloadModel])

  const handleAutoIngest = useCallback(async () => {
    await knowledgeBaseApi.autoIngest()
    await refreshStatus()
    const stats = await knowledgeBaseApi.getStats()
    setKbStats(stats)
  }, [refreshStatus])

  const handleUploadSuccess = useCallback(async () => {
    const stats = await knowledgeBaseApi.getStats()
    setKbStats(stats)
  }, [])

  return (
    <div style={{ display: 'flex', gap: 20, maxHeight: 'calc(100vh - 112px)', overflowY: 'auto' }}>
      <div style={{ flex: 1 }}>
        <EngineControl
          ragStatus={
            ragStatus ?? {
              engine_loaded: false,
              model_key: '',
              model_name: '',
              reranker_enabled: false,
              reranker_model: '',
              knowledge_base_ready: false,
              available_models: {},
              available_rerankers: {},
            }
          }
          isModelLoading={isModelLoading}
          onLoad={handleLoad}
          onUnload={handleUnload}
        />
      </div>
      <div style={{ flex: 1 }}>
        <KnowledgeBasePanel
          stats={kbStats}
          onAutoIngest={handleAutoIngest}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>
    </div>
  )
}

export default SettingsPage
