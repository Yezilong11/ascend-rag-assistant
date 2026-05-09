import React from 'react'
import { UploadOutlined } from '@ant-design/icons'
import { knowledgeBaseApi } from '@/services/knowledgeBaseApi'
import { MAX_FILE_SIZE } from '@/utils/constants'
import { message } from 'antd'

interface FileUploaderProps {
  onUploadSuccess?: () => void
}

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = React.useState(false)
  const [dragOver, setDragOver] = React.useState(false)

  const handleUpload = async (files: File[]) => {
    const oversized = files.find(f => f.size > MAX_FILE_SIZE)
    if (oversized) {
      message.error('文件大小不能超过50MB')
      return
    }
    setUploading(true)
    try {
      for (const file of files) {
        await knowledgeBaseApi.ingest(file)
        message.success(`${file.name} 导入成功`)
      }
      onUploadSuccess?.()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) void handleUpload(files)
  }

  return (
    <div>
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
          input.multiple = true
          input.accept = '.pdf,.txt,.md,.doc,.docx,.html,.htm,.ppt,.pptx,.csv,.xls,.xlsx,.json,.jsonl'
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
          {uploading ? '上传中...' : '拖拽文件到此处或点击上传'}
        </div>
        <div style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>
          支持 PDF、Word、Excel、PPT、HTML、JSON、CSV 等格式，最大 50MB
        </div>
      </div>
    </div>
  )
}

export default FileUploader
