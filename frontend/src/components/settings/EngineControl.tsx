import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { PoweroffOutlined, ThunderboltOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import ModelSelector from './ModelSelector'
import RerankerConfig from './RerankerConfig'
import type { RAGStatus, ModelLoadRequest } from '@/types/rag'
import { useAppStore } from '@/stores/appStore'

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
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [useReranker, setUseReranker] = useState(false)
  const [rerankerModel, setRerankerModel] = useState<string>('')
  const [rerankerTopK, setRerankerTopK] = useState(3)
  const [initialRetrievalK, setInitialRetrievalK] = useState(10)
  const lastLoadError = useAppStore((s) => s.lastLoadError)
  const setLastLoadError = useAppStore((s) => s.setLastLoadError)

  const modelKeys = useMemo(
    () => Object.keys(ragStatus.available_models || {}),
    [ragStatus.available_models],
  )
  const rerankerKeys = useMemo(
    () => Object.keys(ragStatus.available_rerankers || {}),
    [ragStatus.available_rerankers],
  )

  const effectiveSelectedModel = selectedModel || modelKeys[0] || ''
  const effectiveRerankerModel = rerankerModel || rerankerKeys[0] || ''

  const handleLoad = useCallback(async () => {
    if (!effectiveSelectedModel) return
    await onLoad({
      model_key: effectiveSelectedModel,
      use_reranker: useReranker,
      reranker_model: useReranker ? effectiveRerankerModel : undefined,
      reranker_top_k: useReranker ? rerankerTopK : undefined,
      initial_retrieval_k: initialRetrievalK,
    })
  }, [
    effectiveSelectedModel,
    useReranker,
    effectiveRerankerModel,
    rerankerTopK,
    initialRetrievalK,
    onLoad,
  ])

  const handleUnload = useCallback(async () => {
    await onUnload()
  }, [onUnload])

  // 用户开始新的加载时，清除旧的错误
  useEffect(() => {
    if (isModelLoading) {
      setLastLoadError(null)
    }
  }, [isModelLoading, setLastLoadError])

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
          {lastLoadError && (
            <div
              style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(255, 51, 102, 0.08)',
                border: '1px solid rgba(255, 51, 102, 0.2)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8,
                color: 'var(--neon-red)',
                fontSize: 12,
                lineHeight: 1.5,
                wordBreak: 'break-word',
              }}
            >
              <ExclamationCircleOutlined style={{ marginTop: 2, flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, marginBottom: 2 }}>模型加载失败</div>
                <div style={{ color: 'var(--text-secondary)' }}>{lastLoadError}</div>
              </div>
              <button
                onClick={() => setLastLoadError(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-tertiary)',
                  cursor: 'pointer',
                  fontSize: 14,
                  padding: 0,
                  lineHeight: 1,
                }}
                aria-label="关闭错误"
              >
                ×
              </button>
            </div>
          )}
          <div>
            <div
              style={{
                color: 'var(--text-secondary)',
                fontSize: 12,
                marginBottom: 8,
                fontWeight: 500,
              }}
            >
              选择模型{' '}
              {effectiveSelectedModel && (
                <span style={{ color: 'var(--neon-blue)' }}>✓ 已选择</span>
              )}
            </div>
            <ModelSelector
              availableModels={ragStatus.available_models || {}}
              value={effectiveSelectedModel}
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
              availableRerankers={ragStatus.available_rerankers || {}}
              enabled={useReranker}
              model={effectiveRerankerModel}
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
            disabled={!effectiveSelectedModel}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: effectiveSelectedModel ? 'var(--gradient-primary)' : 'var(--bg-tertiary)',
              border: 'none',
              color: effectiveSelectedModel ? '#fff' : 'var(--text-tertiary)',
              cursor: effectiveSelectedModel ? 'pointer' : 'not-allowed',
              fontSize: 14,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              transition: 'all var(--transition-normal)',
              boxShadow: effectiveSelectedModel ? '0 4px 15px rgba(0, 212, 255, 0.25)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (effectiveSelectedModel) {
                e.currentTarget.style.boxShadow = '0 6px 25px rgba(0, 212, 255, 0.4)'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }
            }}
            onMouseLeave={(e) => {
              if (effectiveSelectedModel) {
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
