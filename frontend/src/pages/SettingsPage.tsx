import React, { useCallback, useEffect, useState } from 'react'
import { message, Switch } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { useRAGStatus } from '@/hooks/useRAGStatus'
import { knowledgeBaseApi } from '@/services/knowledgeBaseApi'
import EngineControl from '@/components/settings/EngineControl'
import KnowledgeBasePanel from '@/components/knowledge/KnowledgeBasePanel'
import { useAppStore } from '@/stores/appStore'
import type { KnowledgeBaseStats, ModelLoadRequest } from '@/types/rag'

const SettingsPage: React.FC = () => {
  const { ragStatus, isModelLoading, loadModel, unloadModel, refreshStatus } = useRAGStatus()
  const [kbStats, setKbStats] = useState<KnowledgeBaseStats | null>(null)
  const vlmEnabled = useAppStore((s) => s.vlmEnabled)
  const setVlmEnabled = useAppStore((s) => s.setVlmEnabled)

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
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, maxHeight: 'calc(100vh - 112px)', overflowY: 'auto' }}>
      <div style={{ flex: 1, minWidth: 300 }}>
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
      <div style={{ flex: 1, minWidth: 300 }}>
        <div className="glass-card-static" style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 10,
                background: 'linear-gradient(135deg, #ff8c00, #ff6b00)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: 16,
                boxShadow: '0 0 12px rgba(255, 140, 0, 0.2)',
              }}
            >
              <EyeOutlined />
            </div>
            <h3
              style={{
                margin: 0,
                fontSize: 16,
                fontWeight: 700,
                background: 'linear-gradient(135deg, #ff8c00, #ff6b00)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              多模态配置
            </h3>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-glass)',
              border: '1px solid var(--border-glass)',
            }}
          >
            <div>
              <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>
                VLM 图片描述
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
                启用后将使用视觉语言模型对图片生成详细描述
              </div>
            </div>
            <Switch checked={vlmEnabled} onChange={setVlmEnabled} />
          </div>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 300 }}>
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
