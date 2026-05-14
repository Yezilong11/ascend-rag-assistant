import React, { useCallback, useState } from 'react'
import {
  PoweroffOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  CloudUploadOutlined,
  DatabaseOutlined,
} from '@ant-design/icons'
import { message, Switch, Modal, Slider } from 'antd'
import { useRAGStatus } from '@/hooks/useRAGStatus'
import { knowledgeBaseApi } from '@/services/knowledgeBaseApi'
import FileUploader from '@/components/knowledge/FileUploader'
import { useAppStore } from '@/stores/appStore'
import type { KnowledgeBaseStats, ModelLoadRequest, ModelInfo, RerankerInfo } from '@/types/rag'

const SettingsPage: React.FC = () => {
  const { ragStatus, loadModel, unloadModel, refreshStatus } = useRAGStatus()
  const [kbStats, setKbStats] = useState<KnowledgeBaseStats | null>(null)
  const vlmEnabled = useAppStore((s) => s.vlmEnabled)
  const setVlmEnabled = useAppStore((s) => s.setVlmEnabled)
  const [autoIngesting, setAutoIngesting] = useState(false)
  const [showModelSelector, setShowModelSelector] = useState(false)
  const [showRerankerSelector, setShowRerankerSelector] = useState(false)
  const [showTopKModal, setShowTopKModal] = useState(false)
  const [showRetrievalKModal, setShowRetrievalKModal] = useState(false)
  const [showVLMModelSelector, setShowVLMModelSelector] = useState(false)

  const [selectedModel, setSelectedModel] = useState<string>('')
  const [useReranker, setUseReranker] = useState(false)
  const [rerankerModel, setRerankerModel] = useState<string>('')
  const [rerankerTopK, setRerankerTopK] = useState(3)
  const [initialRetrievalK, setInitialRetrievalK] = useState(10)
  const [autoIngestEnabled, setAutoIngestEnabled] = useState(true)

  const modelKeys = Object.keys(ragStatus?.available_models || {})
  const rerankerKeys = Object.keys(ragStatus?.available_rerankers || {})
  const effectiveSelectedModel = selectedModel || modelKeys[0] || ragStatus?.model_key || ''
  const effectiveRerankerModel = rerankerModel || rerankerKeys[0] || ''
  const selectedModelInfo = ragStatus?.available_models?.[effectiveSelectedModel]
  const selectedRerankerInfo = ragStatus?.available_rerankers?.[effectiveRerankerModel]

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
    setAutoIngesting(true)
    try {
      await knowledgeBaseApi.autoIngest()
      message.success('自动导入完成')
      await refreshStatus()
      const stats = await knowledgeBaseApi.getStats()
      setKbStats(stats)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setAutoIngesting(false)
    }
  }, [refreshStatus])

  const handleUploadSuccess = useCallback(async () => {
    const stats = await knowledgeBaseApi.getStats()
    setKbStats(stats)
  }, [])

  const handleStartEngine = async () => {
    if (!effectiveSelectedModel) return
    await handleLoad({
      model_key: effectiveSelectedModel,
      use_reranker: useReranker,
      reranker_model: useReranker ? effectiveRerankerModel : undefined,
      reranker_top_k: useReranker ? rerankerTopK : undefined,
      initial_retrieval_k: initialRetrievalK,
    })
  }

  const handleModelSelect = (key: string) => {
    setSelectedModel(key)
    setShowModelSelector(false)
  }

  const handleRerankerSelect = (key: string) => {
    setRerankerModel(key)
    setShowRerankerSelector(false)
  }

  const isEngineLoaded = ragStatus?.engine_loaded || false

  return (
    <div
      style={{
        maxWidth: 900,
        margin: '0 auto',
        padding: '24px 20px',
        overflowY: 'auto',
        maxHeight: 'calc(100vh - 112px)',
      }}
    >
      {/* 分组1：AI引擎控制 */}
      <div
        style={{
          background: '#1C1C1E',
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 500,
            color: '#f0f4ff',
            padding: '16px 20px 12px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <ThunderboltOutlined style={{ marginRight: 8 }} /> AI引擎控制
        </div>

        {/* 引擎状态 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>引擎状态</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: isEngineLoaded ? '#00ff88' : '#5a6380',
                boxShadow: isEngineLoaded ? '0 0 6px #00ff88' : 'none',
              }}
            />
            <span style={{ fontSize: 15, color: isEngineLoaded ? '#00ff88' : '#8E8E93' }}>
              {isEngineLoaded ? '系统运行中' : '引擎已停止'}
            </span>
          </div>
        </div>

        {/* 当前模型 */}
        <div
          onClick={() => !isEngineLoaded && setShowModelSelector(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
            cursor: isEngineLoaded ? 'default' : 'pointer',
            background: isEngineLoaded ? 'transparent' : 'transparent',
          }}
          onMouseEnter={(e) => {
            if (!isEngineLoaded) e.currentTarget.style.background = '#2C2C2E'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>当前模型</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>
              {isEngineLoaded ? ragStatus?.model_name || '-' : selectedModelInfo?.name || '未选择'}
            </span>
            {!isEngineLoaded && <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>}
          </div>
        </div>

        {/* 重排序状态 */}
        <div
          onClick={() => setShowRerankerSelector(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = '#2C2C2E')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>重排序状态</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>
              {isEngineLoaded
                ? ragStatus?.reranker_enabled
                  ? '已启用'
                  : '未启用'
                : useReranker
                  ? '已启用'
                  : '未启用'}
            </span>
            <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>
          </div>
        </div>

        {/* 操作按钮 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: 56,
            padding: '0 20px',
          }}
        >
          {isEngineLoaded ? (
            <button
              onClick={() => void handleUnload()}
              style={{
                width: '100%',
                height: 40,
                borderRadius: 8,
                background: 'rgba(255, 51, 102, 0.08)',
                border: '1px solid rgba(255, 51, 102, 0.2)',
                color: '#ff3366',
                cursor: 'pointer',
                fontSize: 14,
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
              }}
            >
              <PoweroffOutlined /> 停止AI引擎
            </button>
          ) : (
            <button
              onClick={() => void handleStartEngine()}
              disabled={!effectiveSelectedModel}
              style={{
                width: '100%',
                height: 40,
                borderRadius: 8,
                background: effectiveSelectedModel
                  ? 'linear-gradient(135deg, #00d4ff 0%, #7b2fff 100%)'
                  : '#1a1f35',
                border: 'none',
                color: effectiveSelectedModel ? '#fff' : '#5a6380',
                cursor: effectiveSelectedModel ? 'pointer' : 'not-allowed',
                fontSize: 14,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
              }}
            >
              <PoweroffOutlined /> 启动AI引擎
            </button>
          )}
        </div>
      </div>

      {/* 分组2：多模态配置 */}
      <div
        style={{
          background: '#1C1C1E',
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 500,
            color: '#f0f4ff',
            padding: '16px 20px 12px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <EyeOutlined style={{ marginRight: 8 }} /> 多模态配置
        </div>

        {/* VLM图片描述 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            padding: '14px 20px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <div>
            <div style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0', marginBottom: 4 }}>
              VLM图片描述
            </div>
            <div style={{ fontSize: 13, color: '#8E8E93' }}>
              启用后将使用视觉语言模型对图片生成详细描述
            </div>
          </div>
          <Switch checked={vlmEnabled} onChange={setVlmEnabled} style={{ marginTop: 4 }} />
        </div>

        {/* 图片描述模型 */}
        <div
          onClick={() => setShowVLMModelSelector(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = '#2C2C2E')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>图片描述模型</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>-</span>
            <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>
          </div>
        </div>

        {/* 知识库统计 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>知识库统计</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ fontSize: 15, color: '#00d4ff' }}>
              文档数: {kbStats?.document_count ?? '-'}
            </span>
            <span style={{ color: '#5a6380', margin: '0 4px' }}>|</span>
            <span style={{ fontSize: 15, color: '#7b2fff' }}>
              分块数: {kbStats?.chunk_count ?? '-'}
            </span>
            <span style={{ color: '#5a6380', margin: '0 4px' }}>|</span>
            <span style={{ fontSize: 15, color: '#ff8c00' }}>
              图片块数: {kbStats?.image_chunk_count ?? '-'}
            </span>
          </div>
        </div>
      </div>

      {/* 分组3：多模态知识库管理 */}
      <div
        style={{
          background: '#1C1C1E',
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 500,
            color: '#f0f4ff',
            padding: '16px 20px 12px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <DatabaseOutlined style={{ marginRight: 8 }} /> 多模态知识库管理
        </div>

        {/* 上传文件 */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #2C2C2E' }}>
          <div style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0', marginBottom: 12 }}>
            上传文件
          </div>
          <FileUploader onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* 知识库映射说明 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>知识库映射</span>
          <span style={{ fontSize: 14, color: '#8E8E93' }}>
            文档 → 主知识库 | 图片 → 多模态知识库（OCR）
          </span>
        </div>
      </div>

      {/* 分组4：重排序配置 */}
      <div
        style={{
          background: '#1C1C1E',
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 500,
            color: '#f0f4ff',
            padding: '16px 20px 12px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <ThunderboltOutlined style={{ marginRight: 8 }} /> 重排序配置
        </div>

        {/* 启用重排序 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>启用重排序</span>
          <Switch checked={useReranker} onChange={setUseReranker} />
        </div>

        {/* 重排序模型 */}
        <div
          onClick={() => useReranker && setShowRerankerSelector(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
            cursor: useReranker ? 'pointer' : 'default',
            opacity: useReranker ? 1 : 0.5,
          }}
          onMouseEnter={(e) => {
            if (useReranker) e.currentTarget.style.background = '#2C2C2E'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>重排序模型</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>
              {selectedRerankerInfo?.name ||
                (rerankerKeys[0]
                  ? ragStatus?.available_rerankers?.[rerankerKeys[0]]?.name
                  : '未选择')}
            </span>
            {useReranker && <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>}
          </div>
        </div>

        {/* Top K */}
        <div
          onClick={() => useReranker && setShowTopKModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            borderBottom: '1px solid #2C2C2E',
            cursor: useReranker ? 'pointer' : 'default',
            opacity: useReranker ? 1 : 0.5,
          }}
          onMouseEnter={(e) => {
            if (useReranker) e.currentTarget.style.background = '#2C2C2E'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>Top K</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>{rerankerTopK}</span>
            {useReranker && <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>}
          </div>
        </div>

        {/* 初始检索数量 */}
        <div
          onClick={() => setShowRetrievalKModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = '#2C2C2E')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>初始检索数量</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 15, color: '#8E8E93' }}>{initialRetrievalK}</span>
            <span style={{ color: '#8E8E93', fontSize: 18 }}>›</span>
          </div>
        </div>
      </div>

      {/* 分组5：其他设置 */}
      <div
        style={{
          background: '#1C1C1E',
          borderRadius: 16,
          marginBottom: 24,
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 500,
            color: '#f0f4ff',
            padding: '16px 20px 12px',
            borderBottom: '1px solid #2C2C2E',
          }}
        >
          <SettingOutlined style={{ marginRight: 8 }} /> 其他设置
        </div>

        {/* 自动导入知识库 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 56,
            padding: '0 20px',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 450, color: '#F0F0F0' }}>自动导入知识库</span>
          <Switch checked={autoIngestEnabled} onChange={setAutoIngestEnabled} />
        </div>
      </div>

      {/* 自动导入按钮 */}
      <button
        onClick={() => void handleAutoIngest()}
        disabled={autoIngesting || !autoIngestEnabled}
        style={{
          width: '100%',
          height: 44,
          borderRadius: 8,
          background: autoIngestEnabled && !autoIngesting ? 'rgba(0, 255, 136, 0.08)' : '#1a1f35',
          border: '1px solid rgba(0, 255, 136, 0.2)',
          color: autoIngestEnabled && !autoIngesting ? '#00ff88' : '#5a6380',
          cursor: autoIngestEnabled && !autoIngesting ? 'pointer' : 'not-allowed',
          fontSize: 14,
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
          marginTop: 8,
        }}
      >
        <CloudUploadOutlined /> {autoIngesting ? '导入中...' : '自动导入知识库'}
      </button>

      {/* 模型选择弹窗 */}
      <Modal
        title="选择模型"
        open={showModelSelector}
        onCancel={() => setShowModelSelector(false)}
        footer={null}
        width={400}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {modelKeys.map((key) => {
            const info = ragStatus?.available_models?.[key] as ModelInfo | undefined
            const isSelected = effectiveSelectedModel === key
            return (
              <div
                key={key}
                onClick={() => handleModelSelect(key)}
                style={{
                  padding: '12px 16px',
                  borderRadius: 8,
                  background: isSelected ? 'rgba(0, 212, 255, 0.08)' : '#1a1f35',
                  border: isSelected ? '1px solid rgba(0, 212, 255, 0.3)' : '1px solid #2C2C2E',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: 600, color: '#f0f4ff', fontSize: 14 }}>
                  {info?.name || key}
                </div>
                <div style={{ color: '#8E8E93', fontSize: 12 }}>{info?.description || ''}</div>
              </div>
            )
          })}
        </div>
      </Modal>

      {/* 重排序模型选择弹窗 */}
      <Modal
        title="选择重排序模型"
        open={showRerankerSelector}
        onCancel={() => setShowRerankerSelector(false)}
        footer={null}
        width={400}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {rerankerKeys.map((key) => {
            const info = ragStatus?.available_rerankers?.[key] as RerankerInfo | undefined
            const isSelected = effectiveRerankerModel === key
            return (
              <div
                key={key}
                onClick={() => handleRerankerSelect(key)}
                style={{
                  padding: '12px 16px',
                  borderRadius: 8,
                  background: isSelected ? 'rgba(123, 47, 255, 0.08)' : '#1a1f35',
                  border: isSelected ? '1px solid rgba(123, 47, 255, 0.3)' : '1px solid #2C2C2E',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: 600, color: '#f0f4ff', fontSize: 14 }}>
                  {info?.name || key}
                </div>
                <div style={{ color: '#8E8E93', fontSize: 12 }}>{info?.size || ''}</div>
              </div>
            )
          })}
        </div>
      </Modal>

      {/* Top K 调节弹窗 */}
      <Modal
        title="Top K"
        open={showTopKModal}
        onCancel={() => setShowTopKModal(false)}
        footer={null}
        width={360}
      >
        <div style={{ padding: '20px 0' }}>
          <div
            style={{
              textAlign: 'center',
              fontSize: 32,
              fontWeight: 600,
              color: '#00d4ff',
              marginBottom: 20,
            }}
          >
            {rerankerTopK}
          </div>
          <Slider
            min={1}
            max={10}
            value={rerankerTopK}
            onChange={setRerankerTopK}
            style={{ margin: '0 8px' }}
          />
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              color: '#8E8E93',
              fontSize: 12,
              marginTop: 8,
            }}
          >
            <span>1</span>
            <span>10</span>
          </div>
        </div>
      </Modal>

      {/* 初始检索数量调节弹窗 */}
      <Modal
        title="初始检索数量"
        open={showRetrievalKModal}
        onCancel={() => setShowRetrievalKModal(false)}
        footer={null}
        width={360}
      >
        <div style={{ padding: '20px 0' }}>
          <div
            style={{
              textAlign: 'center',
              fontSize: 32,
              fontWeight: 600,
              color: '#7b2fff',
              marginBottom: 20,
            }}
          >
            {initialRetrievalK}
          </div>
          <Slider
            min={3}
            max={30}
            value={initialRetrievalK}
            onChange={setInitialRetrievalK}
            style={{ margin: '0 8px' }}
          />
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              color: '#8E8E93',
              fontSize: 12,
              marginTop: 8,
            }}
          >
            <span>3</span>
            <span>30</span>
          </div>
        </div>
      </Modal>

      {/* VLM模型选择弹窗 */}
      <Modal
        title="选择VLM模型"
        open={showVLMModelSelector}
        onCancel={() => setShowVLMModelSelector(false)}
        footer={null}
        width={400}
      >
        <div style={{ color: '#8E8E93', textAlign: 'center', padding: '20px 0' }}>
          暂无可用的VLM模型
        </div>
      </Modal>
    </div>
  )
}

export default SettingsPage

function SettingOutlined({ style }: { style?: React.CSSProperties }) {
  return <span style={{ fontSize: 16, ...style }}>⚙</span>
}
