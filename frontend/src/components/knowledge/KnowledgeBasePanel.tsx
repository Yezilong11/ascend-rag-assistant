import React, { useState } from 'react'
import { CloudUploadOutlined, DatabaseOutlined } from '@ant-design/icons'
import { message } from 'antd'
import type { KnowledgeBaseStats } from '@/types/rag'
import FileUploader from './FileUploader'

interface KnowledgeBasePanelProps {
  stats: KnowledgeBaseStats | null
  onAutoIngest: () => Promise<void>
  onUploadSuccess?: () => void
  imageChunkCount?: number
}

const KnowledgeBasePanel: React.FC<KnowledgeBasePanelProps> = ({
  stats,
  onAutoIngest,
  onUploadSuccess,
  imageChunkCount,
}) => {
  const [autoIngesting, setAutoIngesting] = useState(false)

  const handleAutoIngest = async () => {
    setAutoIngesting(true)
    try {
      await onAutoIngest()
      message.success('自动导入完成')
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setAutoIngesting(false)
    }
  }

  const isReady = stats?.status === 'ready'

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
            background: 'var(--gradient-accent)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 16,
            boxShadow: '0 0 12px rgba(0, 255, 136, 0.2)',
          }}
        >
          <DatabaseOutlined />
        </div>
        <h3
          style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 700,
            background: 'var(--gradient-accent)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          多模态知识库管理
        </h3>
      </div>

      {stats && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr 1fr',
            gap: 12,
            marginBottom: 20,
          }}
        >
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              background: isReady ? 'rgba(0, 255, 136, 0.06)' : 'rgba(255, 184, 0, 0.06)',
              border: `1px solid ${isReady ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 184, 0, 0.15)'}`,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 4 }}>状态</div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 4,
                fontWeight: 600,
                color: isReady ? 'var(--neon-green)' : 'var(--neon-amber)',
                fontSize: 13,
              }}
            >
              <div
                className={`glow-dot ${isReady ? 'glow-dot-green' : ''}`}
                style={{
                  width: 5,
                  height: 5,
                  background: isReady ? 'var(--neon-green)' : 'var(--neon-amber)',
                }}
              />
              {isReady ? '就绪' : '初始化中'}
            </div>
          </div>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(0, 212, 255, 0.06)',
              border: '1px solid rgba(0, 212, 255, 0.15)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 4 }}>文档数</div>
            <div style={{ fontWeight: 700, color: 'var(--neon-blue)', fontSize: 18 }}>
              {stats.document_count}
            </div>
          </div>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(123, 47, 255, 0.06)',
              border: '1px solid rgba(123, 47, 255, 0.15)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 4 }}>分块数</div>
            <div style={{ fontWeight: 700, color: 'var(--neon-purple)', fontSize: 18 }}>
              {stats.chunk_count}
            </div>
          </div>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(255, 140, 0, 0.06)',
              border: '1px solid rgba(255, 140, 0, 0.15)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 4 }}>图片块数</div>
            <div style={{ fontWeight: 700, color: '#ff8c00', fontSize: 18 }}>
              {imageChunkCount ?? '-'}
            </div>
          </div>
        </div>
      )}

      <FileUploader onUploadSuccess={onUploadSuccess} />

      <button
        onClick={() => void handleAutoIngest()}
        disabled={autoIngesting}
        style={{
          width: '100%',
          marginTop: 12,
          padding: '10px 16px',
          borderRadius: 'var(--radius-sm)',
          background: autoIngesting ? 'var(--bg-tertiary)' : 'rgba(0, 255, 136, 0.08)',
          border: '1px solid rgba(0, 255, 136, 0.2)',
          color: autoIngesting ? 'var(--text-tertiary)' : 'var(--neon-green)',
          cursor: autoIngesting ? 'not-allowed' : 'pointer',
          fontSize: 13,
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
          transition: 'all var(--transition-normal)',
        }}
        onMouseEnter={(e) => {
          if (!autoIngesting) {
            e.currentTarget.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.15)'
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = 'none'
        }}
      >
        <CloudUploadOutlined /> {autoIngesting ? '导入中...' : '自动导入知识库'}
      </button>
    </div>
  )
}

export default KnowledgeBasePanel
