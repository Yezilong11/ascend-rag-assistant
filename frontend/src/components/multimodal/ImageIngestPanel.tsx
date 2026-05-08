import React, { useState } from 'react'
import { PictureOutlined, UploadOutlined } from '@ant-design/icons'
import { Switch, message } from 'antd'
import { multimodalApi } from '@/services/multimodalApi'
import { useAppStore } from '@/stores/appStore'

const ImageIngestPanel: React.FC = () => {
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const vlmEnabled = useAppStore((s) => s.vlmEnabled)
  const setVlmEnabled = useAppStore((s) => s.setVlmEnabled)
  const [lastResult, setLastResult] = useState<{
    success_count: number
    failed_count: number
    total_count: number
  } | null>(null)

  const handleUpload = async (files: File[]) => {
    if (files.length === 0) return
    setUploading(true)
    setLastResult(null)
    try {
      const result = await multimodalApi.ingestImage(files, 'unknown', vlmEnabled)
      setLastResult({
        success_count: result.success_count,
        failed_count: result.failed_count,
        total_count: result.total_count,
      })
      if (result.success) {
        message.success(`成功导入 ${result.success_count} 张图片`)
      } else {
        message.warning(`导入完成：成功 ${result.success_count}，失败 ${result.failed_count}`)
      }
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      /\.(jpg|jpeg|png|gif|bmp)$/i.test(f.name),
    )
    if (files.length > 0) void handleUpload(files)
  }

  return (
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
          <PictureOutlined />
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
          图片导入
        </h3>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => {
          const input = document.createElement('input')
          input.type = 'file'
          input.accept = '.jpg,.jpeg,.png,.gif,.bmp'
          input.multiple = true
          input.onchange = (e) => {
            const files = Array.from((e.target as HTMLInputElement).files ?? [])
            if (files.length > 0) void handleUpload(files)
          }
          input.click()
        }}
        style={{
          border: `2px dashed ${dragOver ? 'var(--neon-blue)' : 'var(--border-glass)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '24px 16px',
          textAlign: 'center',
          cursor: uploading ? 'wait' : 'pointer',
          background: dragOver ? 'rgba(0, 212, 255, 0.04)' : 'var(--bg-glass)',
          transition: 'all var(--transition-normal)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
        }}
      >
        <UploadOutlined
          style={{
            fontSize: 28,
            color: dragOver ? 'var(--neon-blue)' : 'var(--text-tertiary)',
            marginBottom: 8,
            display: 'block',
          }}
        />
        <div style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 4 }}>
          {uploading ? '上传处理中...' : '拖拽图片到此处或点击上传'}
        </div>
        <div style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>
          支持 JPG、PNG、GIF、BMP 格式，可多选
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          marginTop: 12,
        }}
      >
        <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>VLM 图片描述</span>
        <Switch size="small" checked={vlmEnabled} onChange={setVlmEnabled} />
      </div>

      {lastResult && (
        <div
          style={{
            marginTop: 12,
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            background: lastResult.failed_count === 0 ? 'rgba(0, 255, 136, 0.06)' : 'rgba(255, 184, 0, 0.06)',
            border: `1px solid ${lastResult.failed_count === 0 ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 184, 0, 0.15)'}`,
            fontSize: 12,
            color: 'var(--text-secondary)',
          }}
        >
          上次导入：共 {lastResult.total_count} 张，成功 {lastResult.success_count} 张
          {lastResult.failed_count > 0 && `，失败 ${lastResult.failed_count} 张`}
        </div>
      )}
    </div>
  )
}

export default ImageIngestPanel
