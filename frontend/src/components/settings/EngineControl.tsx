import React, { useState, useCallback } from 'react'
import { PoweroffOutlined, ThunderboltOutlined } from '@ant-design/icons'
import ModelSelector from './ModelSelector'
import RerankerConfig from './RerankerConfig'
import type { RAGStatus, ModelLoadRequest } from '@/types/rag'

interface EngineControlProps {
  ragStatus: RAGStatus
  isModelLoading: boolean
  onLoad: (request: ModelLoadRequest) => Promise<void>
  onUnload: () => Promise<void>
}

const EngineControl: React.FC<EngineControlProps> = ({
  ragStatus,
  isModelLoading,
  onLoad,
  onUnload,
}) => {
  const [selectedModel, setSelectedModel] = useState(ragStatus.model_key || '')
  const [useReranker, setUseReranker] = useState(ragStatus.reranker_enabled)
  const [rerankerModel, setRerankerModel] = useState(ragStatus.reranker_model || '')
  const [rerankerTopK, setRerankerTopK] = useState(3)
  const [initialRetrievalK, setInitialRetrievalK] = useState(10)

  const handleLoad = useCallback(async () => {
    await onLoad({
      model_key: selectedModel,
      use_reranker: useReranker,
      reranker_model: useReranker ? rerankerModel : undefined,
      reranker_top_k: useReranker ? rerankerTopK : undefined,
      initial_retrieval_k: initialRetrievalK,
    })
  }, [selectedModel, useReranker, rerankerModel, rerankerTopK, initialRetrievalK, onLoad])

  const handleUnload = useCallback(async () => {
    await onUnload()
  }, [onUnload])

  if (isModelLoading) {
    return (
      <div className="glass-card-static" style={{ padding: 20, textAlign: 'center' }}>
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            border: '3px solid var(--border-glass)',
            borderTopColor: 'var(--neon-blue)',
            animation: 'rotateGlow 1s linear infinite',
            margin: '0 auto 16px',
          }}
        />
        <div style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 4 }}>
          模型加载中
        </div>
        <div style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>
          请稍候，正在初始化AI引擎...
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card-static" style={{ padding: 20 }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          marginBottom: 20,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 10,
            background: ragStatus.engine_loaded
              ? 'var(--gradient-accent)'
              : 'var(--gradient-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 16,
            boxShadow: ragStatus.engine_loaded
              ? '0 0 12px rgba(0, 255, 136, 0.3)'
              : '0 0 12px rgba(0, 212, 255, 0.2)',
          }}
        >
          <ThunderboltOutlined />
        </div>
        <h3
          style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 700,
            background: ragStatus.engine_loaded
              ? 'var(--gradient-accent)'
              : 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          AI引擎控制
        </h3>
      </div>

      {ragStatus.engine_loaded ? (
        <div>
          <div
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(0, 255, 136, 0.06)',
              border: '1px solid rgba(0, 255, 136, 0.15)',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}
          >
            <div className="glow-dot glow-dot-green" style={{ width: 8, height: 8 }} />
            <div>
              <div style={{ color: 'var(--neon-green)', fontWeight: 600, fontSize: 13 }}>
                引擎已启动
              </div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>
                当前模型: {ragStatus.model_name} | 重排序:{' '}
                {ragStatus.reranker_enabled ? '已启用' : '未启用'}
              </div>
            </div>
          </div>
          <button
            onClick={() => void handleUnload()}
            style={{
              width: '100%',
              padding: '10px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(255, 51, 102, 0.08)',
              border: '1px solid rgba(255, 51, 102, 0.2)',
              color: 'var(--neon-red)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              transition: 'all var(--transition-normal)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 0 15px rgba(255, 51, 102, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <PoweroffOutlined /> 停止AI引擎
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <div
              style={{
                color: 'var(--text-secondary)',
                fontSize: 12,
                marginBottom: 8,
                fontWeight: 500,
              }}
            >
              选择模型
            </div>
            <ModelSelector
              availableModels={ragStatus.available_models}
              value={selectedModel}
              onChange={setSelectedModel}
            />
          </div>

          <div>
            <div
              style={{
                color: 'var(--text-secondary)',
                fontSize: 12,
                marginBottom: 8,
                fontWeight: 500,
              }}
            >
              重排序配置
            </div>
            <RerankerConfig
              availableRerankers={ragStatus.available_rerankers}
              enabled={useReranker}
              model={rerankerModel}
              topK={rerankerTopK}
              onEnabledChange={setUseReranker}
              onModelChange={setRerankerModel}
              onTopKChange={setRerankerTopK}
            />
          </div>

          <div>
            <div
              style={{
                color: 'var(--text-secondary)',
                fontSize: 12,
                marginBottom: 8,
                fontWeight: 500,
              }}
            >
              初始检索数量: {initialRetrievalK}
            </div>
            <input
              type="range"
              min={3}
              max={30}
              value={initialRetrievalK}
              onChange={(e) => setInitialRetrievalK(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--neon-blue)' }}
            />
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 10,
                color: 'var(--text-tertiary)',
              }}
            >
              <span>3</span>
              <span>30</span>
            </div>
          </div>

          <button
            onClick={() => void handleLoad()}
            disabled={!selectedModel}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: selectedModel ? 'var(--gradient-primary)' : 'var(--bg-tertiary)',
              border: 'none',
              color: selectedModel ? '#fff' : 'var(--text-tertiary)',
              cursor: selectedModel ? 'pointer' : 'not-allowed',
              fontSize: 14,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              transition: 'all var(--transition-normal)',
              boxShadow: selectedModel ? '0 4px 15px rgba(0, 212, 255, 0.25)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (selectedModel) {
                e.currentTarget.style.boxShadow = '0 6px 25px rgba(0, 212, 255, 0.4)'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }
            }}
            onMouseLeave={(e) => {
              if (selectedModel) {
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 212, 255, 0.25)'
                e.currentTarget.style.transform = 'translateY(0)'
              }
            }}
          >
            <PoweroffOutlined /> 启动AI引擎
          </button>
        </div>
      )}
    </div>
  )
}

export default EngineControl
