import React, { useState } from 'react'
import { FilePdfOutlined, UploadOutlined } from '@ant-design/icons'
import { Switch, message } from 'antd'
import { multimodalApi } from '@/services/multimodalApi'
import { useAppStore } from '@/stores/appStore'

const PDFIngestPanel: React.FC = () => {
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [extractImages, setExtractImages] = useState(true)
  const vlmEnabled = useAppStore((s) => s.vlmEnabled)
  const setVlmEnabled = useAppStore((s) => s.setVlmEnabled)
  const [lastResult, setLastResult] = useState<{
    image_chunks_count: number
    extracted_images_count: number
  } | null>(null)

  const handleUpload = async (file: File) => {
    setUploading(true)
    setLastResult(null)
    try {
      const result = await multimodalApi.ingestPdf(file, 'unknown', extractImages, vlmEnabled)
      setLastResult({
        image_chunks_count: result.image_chunks_count,
        extracted_images_count: result.extracted_images_count,
      })
      if (result.success) {
        message.success(
          `PDF导入成功，提取 ${result.extracted_images_count} 张图片，生成 ${result.image_chunks_count} 个图片块`,
        )
      } else {
        message.warning('PDF导入部分失败')
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
    const file = e.dataTransfer.files[0]
    if (file && /\.pdf$/i.test(file.name)) {
      void handleUpload(file)
    } else {
      message.warning('请上传 PDF 文件')
    }
  }

  return (
    <div className="glass-card-static" style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 10,
            background: 'linear-gradient(135deg, #7b2fff, #5b1fd4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 16,
            boxShadow: '0 0 12px rgba(123, 47, 255, 0.2)',
          }}
        >
          <FilePdfOutlined />
        </div>
        <h3
          style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 700,
            background: 'linear-gradient(135deg, #7b2fff, #5b1fd4)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          PDF 多模态导入
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
          input.accept = '.pdf'
          input.onchange = (e) => {
            const file = (e.target as HTMLInputElement).files?.[0]
            if (file) void handleUpload(file)
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
          {uploading ? '处理中...' : '拖拽 PDF 到此处或点击上传'}
        </div>
        <div style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>
          自动提取 PDF 内嵌图片并导入知识库
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          marginTop: 12,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-glass)',
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>提取内嵌图片</span>
          <Switch size="small" checked={extractImages} onChange={setExtractImages} />
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-glass)',
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>VLM 图片描述</span>
          <Switch size="small" checked={vlmEnabled} onChange={setVlmEnabled} />
        </div>
      </div>

      {lastResult && (
        <div
          style={{
            marginTop: 12,
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(123, 47, 255, 0.06)',
            border: '1px solid rgba(123, 47, 255, 0.15)',
            fontSize: 12,
            color: 'var(--text-secondary)',
          }}
        >
          上次导入：提取 {lastResult.extracted_images_count} 张图片，生成 {lastResult.image_chunks_count} 个图片块
        </div>
      )}
    </div>
  )
}

export default PDFIngestPanel
